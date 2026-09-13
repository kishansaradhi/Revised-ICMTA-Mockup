/**
 * ICMTA Faculty Directory — Automatic Photo Synchronizer
 *
 * Scans image directories (images/new, images/existing, images) and
 * automatically links each photo file to the respective faculty member
 * in js/member-data.js based on Member ID or Faculty Name.
 *
 * Usage:
 *   node sync_photos.js
 */

const fs = require('fs');
const path = require('path');

const cwd = path.resolve(__dirname, '..');
const memberDataFile = path.resolve(__dirname, 'member-data.js');
const appJsFile = path.resolve(__dirname, 'app.js');

if (!fs.existsSync(memberDataFile)) {
  console.error('Error: member-data.js not found.');
  process.exit(1);
}

// 1. Load current master data
global.window = {};
require(memberDataFile);
const members = global.window.ICMTA_MASTER_DATA;
console.log(`Loaded ${members.length} members from master data.\n`);

function normalizeName(name) {
  return String(name || '')
    .toLowerCase()
    .replace(/^(?:lt\.?\s*dr\.?|dr\.?|mr\.?|mrs\.?|ms\.?|miss|prof\.?|professor)\s+/i, '')
    .replace(/[^a-z0-9]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function matchPhotoToMember(filename, memberList) {
  if (!filename) return null;
  const raw = String(filename).replace(/\\/g, '/');
  const base = raw.split('/').pop().replace(/\.[^/.]+$/, '');
  
  // 1. Explicit ICMTA ID in filename (e.g. ICMTA107.jpg, ICMTA-001.png, ICMTA_045.jpeg)
  const ICMTAMatch = base.match(/ICMTA[\-_]?(\d+)/i);
  if (ICMTAMatch) {
    const num = parseInt(ICMTAMatch[1], 10);
    const targetId = 'ICMTA' + String(num).padStart(3, '0');
    const member = memberList.find(m => String(m.id).toUpperCase() === targetId);
    if (member) {
      return { member, reason: 'Member ID (' + targetId + ')', confidence: 1.0 };
    }
  }

  // 2. Extract name part from filename (stripping numeric prefixes like 001_, 123-, etc.)
  let cleanName = base
    .replace(/^(?:ICMTA[\-_]?\d+|\d{1,4})[_\-\s]*/i, '')
    .replace(/[_\-]+/g, ' ')
    .trim();
  
  const normFile = normalizeName(cleanName);

  // 3. Name matching:
  if (normFile && normFile.length >= 3) {
    // Exact normalized name match
    let matched = memberList.find(m => normalizeName(m.name) === normFile);
    if (matched) {
      return { member: matched, reason: 'Faculty Name Match ("' + matched.name + '")', confidence: 0.98 };
    }

    // Substring / contained name match
    matched = memberList.find(m => {
      const mn = normalizeName(m.name);
      return mn && (mn === normFile || mn.includes(normFile) || normFile.includes(mn));
    });
    if (matched) {
      return { member: matched, reason: 'Faculty Name Match ("' + matched.name + '")', confidence: 0.90 };
    }

    // Multi-token overlap matching (at least 2 matching significant words)
    const fileTokens = normFile.split(' ').filter(t => t.length > 2);
    if (fileTokens.length >= 2) {
      let best = null;
      let maxOverlap = 0;
      memberList.forEach(m => {
        const mnTokens = new Set(normalizeName(m.name).split(' '));
        const overlap = fileTokens.filter(t => mnTokens.has(t)).length;
        if (overlap > maxOverlap && overlap >= Math.min(2, fileTokens.length)) {
          maxOverlap = overlap;
          best = m;
        }
      });
      if (best && maxOverlap >= 2) {
        return { member: best, reason: 'Key Name Tokens ("' + best.name + '")', confidence: 0.80 };
      }
    }
  }

  // 4. Fallback: Check if filename is purely numeric (e.g. 107.jpg, 001.png)
  const onlyNumMatch = base.match(/^(\d{1,4})$/);
  if (onlyNumMatch) {
    const num = parseInt(onlyNumMatch[1], 10);
    const targetId = 'ICMTA' + String(num).padStart(3, '0');
    const member = memberList.find(m => String(m.id).toUpperCase() === targetId);
    if (member) {
      return { member, reason: 'Numeric ID fallback (' + targetId + ')', confidence: 0.70 };
    }
  }

  return null;
}

// Collect all image files in images/ directory
function getImagesInDir(dirPath) {
  if (!fs.existsSync(dirPath)) return [];
  const results = [];
  const entries = fs.readdirSync(dirPath, { withFileTypes: true });
  for (const entry of entries) {
    const full = path.join(dirPath, entry.name);
    if (entry.isDirectory()) {
      results.push(...getImagesInDir(full));
    } else if (/\.(png|jpe?g|webp|gif)$/i.test(entry.name)) {
      const rel = path.relative(cwd, full).replace(/\\/g, '/');
      results.push(rel);
    }
  }
  return results;
}

const allImages = getImagesInDir(path.resolve(cwd, 'images'));
console.log(`Found ${allImages.length} image files in images/ folder.`);

let newlyLinked = 0;
let alreadyLinked = 0;
let unmatched = [];

allImages.forEach(imgPath => {
  const match = matchPhotoToMember(imgPath, members);
  if (match) {
    const m = match.member;
    if (m.photo === imgPath) {
      alreadyLinked++;
    } else {
      m.photo = imgPath;
      newlyLinked++;
      console.log(`  [LINKED] ${imgPath} -> ${m.id} (${m.name}) [${match.reason}]`);
    }
  } else {
    unmatched.push(imgPath);
  }
});

console.log('\n--- Sync Summary ---');
console.log(`Newly linked:   ${newlyLinked}`);
console.log(`Already linked: ${alreadyLinked}`);
console.log(`Unmatched:      ${unmatched.length}`);

if (unmatched.length > 0) {
  console.log('\nUnmatched photos (rename with Member ID or Faculty Name to auto-link):');
  unmatched.forEach(u => console.log('  - ' + u));
}

if (newlyLinked > 0) {
  // Save updated member-data.js
  const newContent = 'window.ICMTA_MASTER_DATA = ' + JSON.stringify(members) + ';\n';
  fs.writeFileSync(memberDataFile, newContent, 'utf8');
  console.log('\n✔ Successfully updated js/member-data.js');

  // Bump version in js/app.js
  if (fs.existsSync(appJsFile)) {
    let appJs = fs.readFileSync(appJsFile, 'utf8');
    const newVer = 'combined-343-members-aligned-v' + Date.now();
    appJs = appJs.replace(/const MEMBER_DATA_VERSION = "[^"]+";/, `const MEMBER_DATA_VERSION = "${newVer}";`);
    fs.writeFileSync(appJsFile, appJs, 'utf8');
    console.log(`✔ Bumped data version in js/app.js to ${newVer}`);
  }
} else {
  console.log('\nAll matching photos are already up to date.');
}

