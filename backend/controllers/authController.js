const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const supabase = require("../config/supabaseClient");

async function login(req, res) {
  const { user_id, password } = req.body;

  if (!user_id || !password) {
    return res.status(400).json({ success: false, error: "user_id and password are required." });
  }

  const { data: admin, error } = await supabase
    .from("admin")
    .select("*")
    .eq("user_id", user_id)
    .maybeSingle();

  if (error) return res.status(500).json({ success: false, error: error.message });
  if (!admin) return res.status(401).json({ success: false, error: "Invalid credentials." });

  const valid = await bcrypt.compare(password, admin.password || "");
  if (!valid) return res.status(401).json({ success: false, error: "Invalid credentials." });

  const token = jwt.sign({ sub: admin.user_id }, process.env.JWT_SECRET, { expiresIn: "8h" });
  res.json({ success: true, token, expires_in: "8h" });
}

module.exports = { login };