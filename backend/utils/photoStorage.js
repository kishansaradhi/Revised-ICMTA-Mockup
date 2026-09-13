const supabase = require("../config/supabaseClient");

const BUCKET = "member-photos";

// Uploads a photo for a member and returns its public URL.
// Filename convention: "<memberId>.<ext>" — flat, no subfolders.
async function uploadPhoto(memberId, originalName, buffer, mimetype) {
  const ext = (originalName && originalName.includes("."))
    ? originalName.split(".").pop().toLowerCase()
    : "jpg";
  const path = `${String(memberId).toUpperCase()}.${ext}`;

  const { error } = await supabase.storage
    .from(BUCKET)
    .upload(path, buffer, {
      contentType: mimetype || "image/jpeg",
      upsert: true // overwrite if a file at this exact path already exists
    });

  if (error) throw error;

  const { data } = supabase.storage.from(BUCKET).getPublicUrl(path);
  return data.publicUrl;
}

// Deletes a photo from the bucket given its stored public URL.
// Safe to call with null/undefined — does nothing.
async function deletePhotoByUrl(url) {
  if (!url) return;
  const path = extractPathFromUrl(url);
  if (!path) return;

  const { error } = await supabase.storage.from(BUCKET).remove([path]);
  if (error) console.error("Failed to delete photo from storage:", error.message);
}

// Public URL format:
// https://xxxx.supabase.co/storage/v1/object/public/member-photos/ICMTA001.jpg
function extractPathFromUrl(url) {
  const marker = `/object/public/${BUCKET}/`;
  const idx = url.indexOf(marker);
  if (idx === -1) return null;
  return decodeURIComponent(url.slice(idx + marker.length));
}

module.exports = { uploadPhoto, deletePhotoByUrl, BUCKET };