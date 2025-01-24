import path from 'path';
import fs from 'fs';

// Handler to serve images from top level data directory
export default async function handler(req, res) {
    const { path: imagePathArray } = req.query;

    if (imagePathArray.length != 1) {
        res.status(400).send("Invalid image path");
        return;
    }

    const imagePath = imagePathArray[0];

    const baseDir = path.resolve(process.cwd(), '../../data/Flicker8k_Dataset');
    const filePath = path.join(baseDir, imagePath);

    if (!fs.existsSync(filePath)) {
        res.status(404).send("Image not found");
        return;
    }

    const file = fs.readFileSync(filePath);

    res.setHeader("Content-Type", "image/jpeg");
    res.send(file);
}
