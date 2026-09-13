const supabase = require("../config/supabaseClient");

async function generateNextMemberId() {
  // Fetch all existing member IDs
  const { data, error } = await supabase
      .from("icmt_members")
      .select("member_id");
  if (error) {
    throw new Error(`Failed to read existing member IDs: ${error.message}`);
  }
  let maxIdNum = 0;
  if (data && data.length > 0) {
    for (const row of data) {
      if (row.member_id) {
        // Strip out non-numeric characters (e.g. "ICMT186" -> 186)
        const numericPart = parseInt(row.member_id.replace(/\D/g, ""), 10);
        if (!isNaN(numericPart) && numericPart > maxIdNum) {
          maxIdNum = numericPart;
        }
      }
    }
  }
  // Next sequential number
  const nextNum = maxIdNum + 1;
  // Formats as ICMT001, ICMT042, ICMT187, etc. (minimum 3 digits padding)
  return `ICMT${String(nextNum).padStart(3, "0")}`;
}

module.exports = { generateNextMemberId };