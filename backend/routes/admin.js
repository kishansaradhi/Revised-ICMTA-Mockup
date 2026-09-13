const express = require("express");
const router = express.Router();
const { requireAdmin } = require("../middleware/auth");
const upload = require("../middleware/upload");
const { login } = require("../controllers/authController");
const {
  getDashboard, getDataQuality, getMissingPhotos,
  getIncompleteProfiles, getMemberById, createMember, updateMember, deleteMember
} = require("../controllers/adminController");

router.post("/login", login);

router.get("/dashboard", requireAdmin, getDashboard);
router.get("/data-quality", requireAdmin, getDataQuality);
router.get("/members/missing-photos", requireAdmin, getMissingPhotos);
router.get("/members/incomplete", requireAdmin, getIncompleteProfiles);
router.get("/members/:id", requireAdmin, getMemberById);
router.post("/members", requireAdmin, upload.single("photo"), createMember);
router.put("/members/:id", requireAdmin, upload.single("photo"), updateMember);
router.delete("/members/:id", requireAdmin, deleteMember);

module.exports = router;