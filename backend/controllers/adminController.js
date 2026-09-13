const supabase = require("../config/supabaseClient");
const { uploadPhoto, deletePhotoByUrl } = require("../utils/photoStorage");
const { generateNextMemberId } = require("../utils/generateId");
const {
  computeDashboard, computeDataQuality,
  isComplete, missingFieldsFor
} = require("../utils/memberStats");

async function fetchAllMembers() {
  const { data, error } = await supabase.from("icmt_members").select("*");
  if (error) throw error;
  return data;
}

async function getDashboard(req, res) {
  try {
    const members = await fetchAllMembers();
    res.json({ success: true, data: computeDashboard(members) });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
}

async function getDataQuality(req, res) {
  try {
    const members = await fetchAllMembers();
    res.json({ success: true, data: computeDataQuality(members) });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
}

async function getMissingPhotos(req, res) {
  try {
    const members = await fetchAllMembers();
    const rows = members
      .filter(m => !m.photo_url)
      .map(m => ({
        photo_url: null,
        member_id: m.member_id,
        name: m.name,
        designation: m.designation,
        department: m.department,
        institution: m.institution,
        state_province: m.state_province
      }));
    res.json({ success: true, data: rows });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
}

async function getIncompleteProfiles(req, res) {
  try {
    const members = await fetchAllMembers();
    const rows = members
      .filter(m => !isComplete(m))
      .map(m => ({
        photo_url: m.photo_url,
        member_id: m.member_id,
        name: m.name,
        designation: m.designation,
        department: m.department,
        institution: m.institution,
        state_province: m.state_province,
        missing_fields: missingFieldsFor(m)
      }));
    res.json({ success: true, data: rows });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
}

async function getMemberById(req, res) {
  const { id } = req.params;
  const { data, error } = await supabase
    .from("icmt_members")
    .select("*")
    .eq("member_id", id)
    .maybeSingle();

  if (error) return res.status(500).json({ success: false, error: error.message });
  if (!data) return res.status(404).json({ success: false, error: "Member not found." });

  res.json({ success: true, data });
}

// POST /api/admin/members
// Creates a member. If a photo is attached, it's uploaded to the bucket
// first and the resulting public URL is saved directly on insert.
async function createMember(req, res) {
  const record = { ...req.body };
  delete record.member_id;
  delete record.photo_url; // set below from the actual upload result, not client input

  if (!String(record.name || "").trim()) {
    return res.status(400).json({ success: false, error: "Name is required." });
  }

  if (record.professional_email) {
    const { data: clash } = await supabase
      .from("icmt_members").select("member_id")
      .eq("professional_email", record.professional_email).maybeSingle();
    if (clash) return res.status(409).json({ success: false, error: "Professional email already registered." });
  }

  if (record.mobile) {
    const { data: clash } = await supabase
      .from("icmt_members").select("member_id")
      .eq("mobile", record.mobile).maybeSingle();
    if (clash) return res.status(409).json({ success: false, error: "Mobile number already registered." });
  }

  let newId;
  try {
    newId = await generateNextMemberId();
  } catch (err) {
    return res.status(500).json({ success: false, error: "Could not generate member id: " + err.message });
  }

  record.member_id = newId;

  if (req.file) {
    try {
      record.photo_url = await uploadPhoto(newId, req.file.originalname, req.file.buffer, req.file.mimetype);
    } catch (err) {
      return res.status(500).json({ success: false, error: "Could not upload photo: " + err.message });
    }
  }

  const { data, error } = await supabase
    .from("icmt_members")
    .insert(record)
    .select()
    .maybeSingle();

  if (error) return res.status(500).json({ success: false, error: error.message });

  res.status(201).json({ success: true, data });
}

// PUT /api/admin/members/:id
// If a new photo is sent, deletes the member's current photo (by the URL
// already stored in the DB) before uploading and saving the new one.
async function updateMember(req, res) {
  const { id } = req.params;
  const updates = { ...req.body };

  delete updates.member_id;
  delete updates.photo_url; // never trust client-sent value, set below if a file is present

  const { data: existing, error: findErr } = await supabase
    .from("icmt_members")
    .select("*")
    .eq("member_id", id)
    .maybeSingle();

  if (findErr) return res.status(500).json({ success: false, error: findErr.message });
  if (!existing) return res.status(404).json({ success: false, error: "Member not found." });

  if (updates.professional_email) {
    const { data: clash } = await supabase
      .from("icmt_members").select("member_id")
      .eq("professional_email", updates.professional_email)
      .neq("member_id", id).maybeSingle();
    if (clash) return res.status(409).json({ success: false, error: "Professional email already registered to another member." });
  }

  if (updates.mobile) {
    const { data: clash } = await supabase
      .from("icmt_members").select("member_id")
      .eq("mobile", updates.mobile)
      .neq("member_id", id).maybeSingle();
    if (clash) return res.status(409).json({ success: false, error: "Mobile number already registered to another member." });
  }

  if (req.file) {
    try {
      await deletePhotoByUrl(existing.photo_url); // remove old file from bucket, if any
      updates.photo_url = await uploadPhoto(id, req.file.originalname, req.file.buffer, req.file.mimetype);
    } catch (err) {
      return res.status(500).json({ success: false, error: "Could not update photo: " + err.message });
    }
  }

  const { data, error } = await supabase
    .from("icmt_members")
    .update(updates)
    .eq("member_id", id)
    .select()
    .maybeSingle();

  if (error) return res.status(500).json({ success: false, error: error.message });

  res.json({ success: true, data });
}

// DELETE /api/admin/members/:id
// Reads the member's photo_url before deleting the row, then removes
// that exact object from the bucket.
async function deleteMember(req, res) {
  const { id } = req.params;

  const { data: existing, error: findErr } = await supabase
    .from("icmt_members")
    .select("member_id, photo_url")
    .eq("member_id", id)
    .maybeSingle();

  if (findErr) return res.status(500).json({ success: false, error: findErr.message });
  if (!existing) return res.status(404).json({ success: false, error: "Member not found." });

  const { error } = await supabase.from("icmt_members").delete().eq("member_id", id);
  if (error) return res.status(500).json({ success: false, error: error.message });

  await deletePhotoByUrl(existing.photo_url);

  res.json({ success: true, message: `Member ${id} deleted.` });
}

module.exports = {
  getDashboard, getDataQuality, getMissingPhotos,
  getIncompleteProfiles, getMemberById, createMember, updateMember, deleteMember
};