/* 
    * Handler to forward search queries to running vespa instance.
    * The query will be processed by TextEmbeddingSearcher which will compute an embedding
    * of the query and use it to perform an ANN search.
*/
export default async function handler(req, res) {
    const { method } = req;

    const query = req.query.query;
    const result = await fetch("http://localhost:8080/search/?input="+query+"&timeout=3s");
    const json = await result.json();
    let response = [];

    for (const el of json.root.children) {
        response.push({
            relevance: el.relevance,
            filename: el.fields.image_file_name
        })
    }

    switch (method) {
        case "GET":
            // When the client closes the connection, we stop the stream
            res.status(200).json(response);
        default:
            res.setHeader("Allow", ["GET", "POST"]);
            res.status(405).end(`Method ${method} Not Allowed`);
    }
}

