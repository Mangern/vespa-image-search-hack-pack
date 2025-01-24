#! /usr/bin/env python3
import os
import clip
import torch
import sys

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <model_name> <output_file.onnx>")
        print(f"Example: {sys.argv[0]} ViT-B/32 ./transformer.onnx")
        print(f"Possible model names are:\n    " + "\n    ".join(clip.available_models()))
        exit(1)
    model_name = sys.argv[1]
    output_path = sys.argv[2]
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    model, preprocess = clip.load(model_name, device=device)

    img_size = model.visual.input_resolution

    dummy_image = torch.randn(10, 3, img_size, img_size)

    with torch.no_grad():
        print(f"Running forward pass")
        model.encode_image(dummy_image)
        print(f"Exporting ONNX model")
        torch.onnx.export(
                model.visual, 
                dummy_image, 
                output_path, 
                export_params=True, 
                input_names=["input"], 
                output_names=["output"],
                opset_version=14,
                dynamic_axes={"input":{0:"batch"}, "output":{0:"batch"}}
        )

    # TODO: Export text model?
