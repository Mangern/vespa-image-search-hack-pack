/**
 * ImageEmbeddingProcessor
 *
 * This processor is part of the image_embed_chain defined in services.xml.
 * It takes a JSON payload consisting of Base64 encoded images, 
 * computes their CLIP embedding and feeds the resulting tensors to Vespa.
 * See: https://docs.vespa.ai/en/jdisc/processing.html
 *
 * DISCLAIMER: This is not meant to be a production-ready Processor. It is rather meant as an example
 *             of how to extend Vespa using Java. Care has to be taken to ensure efficient feeding and querying.
 */
package ai.vespa.example;

import java.awt.Graphics2D;
import java.awt.Image;
import java.awt.image.BufferedImage;
import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Base64;
import java.util.logging.Logger;
import java.util.regex.Pattern;

import javax.imageio.ImageIO;

import org.json.JSONArray;
import org.json.JSONObject;

import com.google.inject.Inject;
import com.yahoo.container.jdisc.HttpRequest;
import com.yahoo.docproc.Processing;
import com.yahoo.document.Document;
import com.yahoo.document.DocumentPut;
import com.yahoo.document.DocumentType;
import com.yahoo.document.DocumentTypeManager;
import com.yahoo.document.datatypes.TensorFieldValue;
import com.yahoo.documentapi.DocumentAccess;
import com.yahoo.documentapi.SyncParameters;
import com.yahoo.documentapi.SyncSession;
import com.yahoo.processing.Processor;
import com.yahoo.processing.Request;
import com.yahoo.processing.Response;
import com.yahoo.processing.execution.Execution;
import com.yahoo.tensor.Tensor;
import com.yahoo.tensor.TensorType;

import ai.vespa.models.evaluation.ModelsEvaluator;

public class ImageEmbeddingProcessor extends Processor {
    private static final Logger logger = Logger.getLogger(ImageEmbeddingProcessor.class.getName());

    private final DocumentType imageDocumentType;
    private final ModelsEvaluator modelsEvaluator;
    private final SyncSession documentApiSession;

    private final Tensor TENSOR_MEAN;
    private final Tensor TENSOR_STD;

    private static final int MODEL_IMAGE_SIZE = 224;
    private static final String MODEL_NAME = "visual"; // models/visual.onnx

    @Inject
    public ImageEmbeddingProcessor(
        DocumentTypeManager documentTypeManager, 
        ModelsEvaluator modelsEvaluator,
        DocumentAccess documentAccess
    ) {
        this.imageDocumentType = documentTypeManager.getDocumentType("image_search");
        this.modelsEvaluator = modelsEvaluator;
        this.documentApiSession = documentAccess.createSyncSession(new SyncParameters.Builder().build());

        // Tensors for normalizing image before inference (according to clip model)
        TENSOR_MEAN = Tensor.from("tensor<float>(d1[3]):[0.48145466, 0.4578275, 0.40821073]");
        TENSOR_STD  = Tensor.from("tensor<float>(d1[3]):[0.26862954, 0.26130258, 0.27577711]");
    }

    /*
     * POST json data in the format {"image_file_name": "my-file-name", "image": <base64 string> }
     */
    @Override
    public Response process(Request request, Execution execution) {
        // Parse the request
        HttpRequest httpRequest = HttpRequest.getHttpRequest(request).get();
        Response response = new Response(request);

        BufferedReader reader = new BufferedReader(new InputStreamReader(httpRequest.getData()));
        StringBuilder jsonString = new StringBuilder();
        String line;
        try {
            while ((line = reader.readLine()) != null)
                jsonString.append(line);
        } catch (IOException ex) {
            logger.info("IOException when reading request data: " + ex.getMessage());
            return response;
        }

        JSONArray jsonArray = new JSONArray(jsonString.toString());

        int feedCount = 0;
        int totalCount = jsonArray.length();
        for (Object element : jsonArray) {

            if (!(element instanceof JSONObject)) {
                logger.warning("Invalid json: Expected JSONObject, got: " + element.getClass().toString());
                continue;
            }

            JSONObject json = (JSONObject)element;

            if (!json.has("image_file_name")) {
                throw new RuntimeException("Missing key 'image_file_name' in JSON data");
            }

            if (!json.has("image")) {
                throw new RuntimeException("Missing key 'image' in JSON data");
            }

            String imageFileName = json.getString("image_file_name");
            String base64Image   = json.getString("image");

            // Decode image payload
            BufferedImage bufferedImage;
            try {
                bufferedImage = readImageFromBase64(base64Image);
            } catch(IOException exception) {
                logger.info("IOException when converting image: " + exception.getMessage());
                return response;
            }

            // Resize and convert to float Tensor
            BufferedImage resized = resizeImage(bufferedImage);
            Tensor imageTensor = tensorFromImageData(resized);

            // Apply input normalization
            imageTensor = imageTensor.subtract(TENSOR_MEAN).divide(TENSOR_STD);

            // Perform inference
            Tensor result = modelsEvaluator.evaluatorOf(MODEL_NAME).bind("input", imageTensor).evaluate();

            // Reshape (d0[], d1[512]) to (x[512]) and normalize
            Tensor embedding = Util.slice(result, "d0:0").rename("d1", "x").l2Normalize("x");

            // Convert image file name to an appropriate document id
            String imageId;
            if (imageFileName.contains(".")) {
                imageId = imageFileName.split(Pattern.quote("."))[0];
            } else {
                imageId = imageFileName;
            }

            // Create a document put operation
            Processing processing = new Processing();
            Document document = new Document(this.imageDocumentType, "id:image_search:image_search::"+imageId);

            // See src/main/application/image_search.sd for document type description
            document.setFieldValue("image_file_name", imageFileName);
            document.setFieldValue("vit_b_32_image", new TensorFieldValue(embedding));
            DocumentPut documentPut = new DocumentPut(document);
            processing.addDocumentOperation(documentPut);

            documentApiSession.put(documentPut);

            logger.info("Put document: " + imageId);
            ++feedCount;
        }

        logger.info("Fed " + feedCount + " / " + totalCount + " documents");
        // Optionally we could return a more meaningful response
        return response;
    }

    private BufferedImage readImageFromBase64(String base64Image) throws IOException {
        byte[] imageBytes = Base64.getDecoder().decode(base64Image);
        return ImageIO.read(new ByteArrayInputStream(imageBytes));
    }

    /*
     * Resize an image in a similar way to torchvision Resize.
     * The smallest axis will be scaled to target size, while the longer side
     * will be scaled to match aspect ratio
     */
    private BufferedImage resizeImage(BufferedImage input) {
        int inputWidth = input.getWidth();
        int inputHeight = input.getHeight();

        int targetWidth, targetHeight;
        if (inputWidth > inputHeight) {
            targetHeight = MODEL_IMAGE_SIZE;
            // Scale to aspect ratio
            targetWidth = Math.round(targetHeight * (float)inputWidth / (float)inputHeight);
        } else {
            targetWidth = MODEL_IMAGE_SIZE;
            // Scale to aspect ratio
            targetHeight = Math.round(targetWidth * (float)inputHeight / (float)inputWidth);
        }
        BufferedImage resized = new BufferedImage(targetWidth, targetHeight, input.getType());
        Graphics2D g2d = resized.createGraphics();
        g2d.drawImage(input.getScaledInstance(targetWidth, targetHeight, Image.SCALE_SMOOTH), 0, 0, null);
        g2d.dispose();
        return resized;
    }

    private Tensor tensorFromImageData(BufferedImage image) {
        // Build tensor from image data
        // The first axis is the batch, but we are only using a batch size of 1 here.
        Tensor.Builder tensorBuilder = Tensor.Builder.of(
            TensorType.fromSpec("tensor<float>(d0[1], d1[3], d2[" + MODEL_IMAGE_SIZE + "], d3[" + MODEL_IMAGE_SIZE + "])")
        );

        // Crop out a 224x224 region in case one side is longer.
        // Similar to torchvision CenterCrop
        for (int y = 0; y < MODEL_IMAGE_SIZE; ++y) {
            for (int x = 0; x < MODEL_IMAGE_SIZE; ++x) {
                int pixel = image.getRGB(x, y);
                int b = ((pixel >> 0) & 0xFF);
                int g = ((pixel >> 8) & 0xFF);
                int r = ((pixel >> 16) & 0xFF);

                // cell(value, index_0, index_1, ...)
                tensorBuilder.cell((float)r/255.f, 0, 0, y, x);
                tensorBuilder.cell((float)g/255.f, 0, 1, y, x);
                tensorBuilder.cell((float)b/255.f, 0, 2, y, x);
            }
        }

        return tensorBuilder.build();
    }
}
