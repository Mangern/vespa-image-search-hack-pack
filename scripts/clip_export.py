#! /usr/bin/env python3
import os
import clip
import torch
import sys
import pathlib

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <model_name> <output_dir>")
        print(f"Example: {sys.argv[0]} ViT-B/32 src/main/application/models")
        print(f"Possible model names are:\n    " + "\n    ".join(clip.available_models()))
        exit(1)
    model_name = sys.argv[1]
    output_path = sys.argv[2]
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    model, preprocess = clip.load(model_name, device=device)

    img_size = model.visual.input_resolution

    dummy_image = torch.randn(10, 3, img_size, img_size)

    # Export image embedder
    with torch.no_grad():
        model.forward = model.encode_image
        visual_output = pathlib.Path(output_path).joinpath("visual.onnx")
        print(f"Exporting visual model to: {str(visual_output)}")
        torch.onnx.export(
                model, 
                args=(dummy_image,), 
                f=str(visual_output), 
                export_params=True, 
                input_names=["input"], 
                output_names=["output"],
                opset_version=14,
                dynamic_axes={"input":{0:"batch"}, "output":{0:"batch"}}
        )

    # Export text embedder
    with torch.no_grad():
        model.forward = model.encode_text
        dummy_text = clip.tokenize(["test"])
        transformer_output = pathlib.Path(output_path).joinpath("transformer.onnx")
        print(f"Exporting transformer model to: {str(transformer_output)}")
        torch.onnx.export(
            model,
            args=(dummy_text,),
            f=str(transformer_output),
            export_params=True,
            input_names=["input"],
            output_names=["output"],
            dynamic_axes={"input":{0:"batch"}, "output":{0:"batch"}},
            opset_version=14
        )
