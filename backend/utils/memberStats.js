const REQUIRED_FIELDS = [
  "name", "qualification", "designation", "department",
  "institution", "state_province", "country", "expertise"
];

const PUBLIC_FIELDS = [
  "member_id", "name", "qualification", "designation", "department",
  "institution", "city", "state_province", "country", "expertise", "photo_url"
];

function normalize(v) {
  return String(v || "").trim().toLowerCase();
}

function isComplete(member) {
  return REQUIRED_FIELDS.every(f => String(member[f] ?? "").trim() !== "");
}

function missingFieldsFor(member) {
  return REQUIRED_FIELDS.filter(f => String(member[f] ?? "").trim() === "");
}

function hasPhoto(member) {
  return Boolean(String(member.photo_url || "").trim());
}

function splitMulti(value) {
  return String(value || "").split(",").map(x => x.trim()).filter(Boolean);
}

function designationBucket(designation) {
  const v = normalize(designation);
  const map = {
    "assistant professor": "Assistant Professor",
    "associate professor": "Associate Professor",
    "professor": "Professor",
    "dean": "Dean",
    "research scholar": "Research Scholar",
    "head of the department": "Head of the Department",
    "head of department": "Head of the Department",
    "hod": "Head of the Department",
    "principal": "Principal",
    "director": "Director"
  };
  return map[v] || null;
}

function toSortedArray(counts) {
  return Object.entries(counts)
    .map(([label, count]) => ({ label, count }))
    .sort((a, b) => b.count - a.count);
}

function countBy(members, field) {
  const counts = {};
  members.forEach(m => {
    const key = String(m[field] || "Not specified").trim() || "Not specified";
    counts[key] = (counts[key] || 0) + 1;
  });
  return toSortedArray(counts);
}

function countDesignations(members) {
  const counts = {
    "Assistant Professor": 0, "Associate Professor": 0, "Professor": 0,
    "Dean": 0, "Research Scholar": 0, "Head of the Department": 0,
    "Principal": 0, "Director": 0
  };
  let matched = 0;
  members.forEach(m => {
    const bucket = designationBucket(m.designation);
    if (bucket) { counts[bucket]++; matched++; }
  });
  counts["Not specified"] = members.length - matched;
  return toSortedArray(counts);
}

function countMulti(members, field) {
  const counts = {};
  members.forEach(m => {
    const values = splitMulti(m[field]);
    if (!values.length) {
      counts["Not specified"] = (counts["Not specified"] || 0) + 1;
      return;
    }
    values.forEach(v => { counts[v] = (counts[v] || 0) + 1; });
  });
  return toSortedArray(counts);
}

function computeDashboard(members) {
  const total = members.length;
  const missingPhotos = members.filter(m => !hasPhoto(m)).length;
  const incomplete = members.filter(m => !isComplete(m)).length;
  const scholars = members.filter(m => normalize(m.designation) === "research scholar").length;
  const ap = members.filter(m => normalize(m.state_province) === "andhra pradesh").length;
  const countries = new Set(members.map(m => String(m.country || "").trim()).filter(Boolean)).size;

  return {
    member_stats: {
      total,
      missing_photos: missingPhotos,
      incomplete_profiles: incomplete
    },
    highlights: {
      research_scholars: scholars,
      andhra_pradesh: ap,
      countries_represented: countries
    },
    by_state: countBy(members, "state_province"),
    by_designation: countDesignations(members),
    by_expertise: countMulti(members, "expertise"),
    by_research_guideship: countMulti(members, "research_guideship")
  };
}

function computeDataQuality(members) {
  const total = members.length;
  const missingPhotos = members.filter(m => !hasPhoto(m)).length;
  const completeProfiles = members.filter(isComplete).length;
  const missingInfoFields = members.reduce((sum, m) => sum + missingFieldsFor(m).length, 0);

  const idCounts = {};
  members.forEach(m => {
    const id = String(m.member_id || "").trim().toUpperCase();
    if (id) idCounts[id] = (idCounts[id] || 0) + 1;
  });
  const duplicateIds = Object.values(idCounts).filter(c => c > 1).length;

  const rows = members.map(m => ({
    photo_url: m.photo_url || null,
    member_id: m.member_id,
    name: m.name,
    designation: m.designation,
    institution: m.institution,
    qualification: m.qualification,
    photo_status: !hasPhoto(m) ? "no-photo" : (isComplete(m) ? "complete" : "missing-info")
  }));

  return {
    total_members: total,
    complete_profiles: completeProfiles,
    missing_photos: missingPhotos,
    missing_info_fields: missingInfoFields,
    duplicate_ids: duplicateIds,
    members: rows
  };
}

module.exports = {
  REQUIRED_FIELDS, PUBLIC_FIELDS,
  isComplete, missingFieldsFor, hasPhoto,
  computeDashboard, computeDataQuality
};