const multer = require("multer");

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 5 * 1024 * 1024 }, // 5MB
  fileFilter: (req, file, cb) => {
    const allowed = /jpeg|jpg|png|webp/i;
    if (allowed.test(file.mimetype)) cb(null, true);
    else cb(new Error("Only jpg, png, or webp images are allowed."));
  }
});

module.exports = upload;