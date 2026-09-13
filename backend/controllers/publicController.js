const supabase = require("../config/supabaseClient");
const { PUBLIC_FIELDS } = require("../utils/memberStats");

async function getMembers(req, res) {
  const { data, error } = await supabase
    .from("icmt_members")
    .select(PUBLIC_FIELDS.join(","));

  if (error) return res.status(500).json({ success: false, error: error.message });

  res.json({ success: true, data });
}

module.exports = { getMembers };