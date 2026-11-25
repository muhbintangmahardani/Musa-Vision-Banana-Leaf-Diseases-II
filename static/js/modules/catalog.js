/**
 * Five-class pathogen atlas tab switching, specimen dossier updater, and URL sync.
 */

const DOSSIER_DATA = {
  "black-sigatoka": {
    num: "01",
    title: "Sigatoka Hitam",
    sci: "Pseudocercospora fijiensis",
    severity: "Tinggi: Patogen Utama",
    granularity: "Lesion-Level (Deteksi Lesi)",
    fracCode: "FRAC 3 · FRAC 11 · M01",
    img: "/static/samples/sample_black_sigatoka.jpg",
    shortDesc:
      "Garis nekrotik hitam sejajar pertulangan daun yang cepat meluas membentuk bercak hangus terbakar, mematikan hingga 50% helai daun aktif.",
    symptoms:
      "Bercak garis karat cokelat kemerahan di permukaan bawah daun yang berkembang cepat menjadi bercak nekrotik hitam pekat berlubang di tengah. Daun mengering sebelum waktunya, menyebabkan tandan matang dini dan kualitas buah anjlok drastis.",
    impact:
      "Penyakit jamur paling destruktif pada pisang. Menurunkan luas fotosintesis fungsional secara drastis, memicu fenomena premature ripening (buah matang terlalu awal di pohon) dengan rasa masam, dan dapat menimbulkan kerugian hasil hingga 50 sampai 100%.",
    deleafing:
      "De-leafing wajib: Pangkas helai daun yang terkena lebih dari 30% area lesi, buang ke parit sanitasi dan balikkan helai daun ke bawah tanah untuk menekan pelepasan askospora spora jamur terangkat angin ke kanopi lain.",
    frac:
      "Rotasi sistemik FRAC 3 (DMI Triazol: Difenoconazole / Tebuconazole) dan FRAC 11 (QoI Strobilurin: Azoxystrobin) diselingi kontak protektif FRAC M01/M03 (Mancozeb / Tembaga). Maksimal 2 kali aplikasi berturut-turut untuk mencegah resistensi patogen jamur di kebun.",
  },
  "yellow-sigatoka": {
    num: "02",
    title: "Sigatoka Kuning",
    sci: "Pseudocercospora musae",
    severity: "Moderat: Jamur Daun",
    granularity: "Lesion-Level (Deteksi Lesi)",
    fracCode: "FRAC 3 · M01 · M03",
    img: "/static/samples/sample_yellow_sigatoka.jpg",
    shortDesc:
      "Bercak garis kuning kehijauan yang meluas dengan pusat lesi abu-abu dikelilingi batas halo klorotik kuning pekat khas.",
    symptoms:
      "Bercak kuning memanjang searah tulang rusuk daun, lambat laun membesar menjadi bercak oval dengan bagian tengah abu-abu kering bertepi cokelat tua. Memiliki cincin klorosis kuning yang sangat kontras.",
    impact:
      "Menghambat perkembangan kanopi fotosintesis pada fase vegetatif. Jika infeksi terjadi pada awal pembungaan, jumlah sisir pada tandan buah akan berkurang secara signifikan.",
    deleafing:
      "Sanitasi helai daun bawah yang tua atau mulai menguning. Perbaiki drainase parit kebun untuk menurunkan kelembapan relatif mikroklimat tanah.",
    frac:
      "Semprot fungisida protektif berbahan aktif tembaga (FRAC M01) atau dithiocarbamate (FRAC M03). Rotasikan dengan FRAC 3 triazol pada musim hujan intensitas tinggi.",
  },
  cordana: {
    num: "03",
    title: "Bercak Cordana",
    sci: "Cordana musae",
    severity: "Sekunder: Infeksi Luka",
    granularity: "Lesion-Level (Deteksi Lesi)",
    fracCode: "FRAC M01 · M03 (Protektif)",
    img: "/static/samples/sample_cordana.jpg",
    shortDesc:
      "Bercak oval konsentris berdiameter 1-3 cm dengan tepi cokelat gelap dan lingkaran halo kuning khas di sekeliling lesi.",
    symptoms:
      "Lesi oval atau melingkar dengan pola cincin konsentris (target spot). Pusat lesi mengering menjadi abu-abu kecokelatan dengan batas halo klorotik kuning cerah. Sering muncul pada daun yang terlindung atau berada di bawah kanopi lembap.",
    impact:
      "Bersifat patogen sekunder atau oportunistik yang biasanya menyerang jaringan daun yang telah mengalami stres lingkungan atau luka mekanis akibat gesekan angin.",
    deleafing:
      "Sanitasi pangkas tepi helai daun fungsional yang terinfeksi di bawah kanopi aktif. Bakar atau kubur sisa pangkasan dan pastikan kebersihan pisau sanitasi dengan disinfeksi.",
    frac:
      "Fungisida kontak protektif mancozeb/chlorothalonil (FRAC M03/M05) dikombinasikan dengan perbaikan aerasi kebun. Umumnya tidak memerlukan fungisida sistemik berbiaya tinggi.",
  },
  pestalotiopsis: {
    num: "04",
    title: "Pestalotiopsis",
    sci: "Pestalotiopsis spp.",
    severity: "Tepi Daun: Nekrosis Angin",
    granularity: "Lesion-Level (Deteksi Lesi)",
    fracCode: "FRAC M03 · FRAC M05",
    img: "/static/samples/sample_pestalotiopsis.jpg",
    shortDesc:
      "Lesi nekrotik abu-abu dengan titik hitam (acervuli) sporulasi jamur, sering berawal dari tepi helai daun yang robek akibat terpaan angin kencang.",
    symptoms:
      "Bercak nekrotik tidak teratur dengan bagian tengah memutih atau abu-abu pucat. Terlihat titik-titik hitam kecil (acervuli) di permukaan bercak saat diamati dari dekat. Sering menginfeksi jaringan daun yang robek akibat angin kencang.",
    impact:
      "Menyebabkan robekan helai daun mengering dan mati sebelum waktunya. Menurunkan ketahanan mekanis helaian daun pisang terhadap hembusan angin kebun berikutnya.",
    deleafing:
      "Pangkas helai daun yang terinfeksi berat. Hindari luka mekanis pada helai daun muda dan kurangi gesekan antar pelepah dengan pengaturan jarak tanam teratur.",
    frac:
      "Aplikasi fungisida mancozeb (FRAC M03) atau klorotalonil (FRAC M05). Hindari pemupukan nitrogen berlebih yang menyebabkan jaringan lamina daun terlalu sukulen dan mudah koyak.",
  },
  fresh: {
    num: "05",
    title: "Daun Sehat",
    sci: "Musa spp.",
    severity: "Optimal: Kanopi Sehat",
    granularity: "Leaf-Level (Deteksi Daun)",
    fracCode: "Bebas Fungisida Kimia",
    img: "/static/samples/sample_fresh.jpg",
    shortDesc:
      "Jaringan helai daun hijau segar optimal tanpa lesi nekrotik, mendukung fotosintesis penuh pengisian tandan buah pisang.",
    symptoms:
      "Permukaan helaian daun hijau merata, lamina daun utuh, pertulangan daun kokoh tanpa bercak klorotik atau lesi nekrotik. Indikator kanopi fotosintesis produktif prima.",
    impact:
      "Kondisi ideal kebun. Setiap 1 helai daun fungsional sehat mendukung pertambahan bobot buah dan menjamin pengisian nutrisi tandan pisang hingga panen optimal.",
    deleafing:
      "Pertahankan minimal 8 sampai 10 helai daun fungsional per rumpun saat fase vegetatif dan minimal 6 sampai 8 daun aktif sehat saat pembentukan tandan buah hingga waktu panen tiba.",
    frac:
      "Tidak memerlukan aplikasi fungisida kuratif apapun. Lanjutkan pemupukan berimbang (NPK + Silika) serta pemeliharaan sanitasi gulma rutin di sekitar piringan pohon.",
  },
};

function normalizeKey(key) {
  if (!key) return "black-sigatoka";
  const clean = key.toLowerCase().replace(/_/g, "-");
  if (clean === "healthy") return "fresh";
  if (DOSSIER_DATA[clean]) return clean;
  return "black-sigatoka";
}

export function switchPathogen(rawKey, scrollToTop = false) {
  const key = normalizeKey(rawKey);
  const data = DOSSIER_DATA[key];
  if (!data) return;

  document.querySelectorAll(".catalog-tab-btn").forEach((btn) => {
    btn.classList.remove("is-active");
  });
  const activeTab = document.getElementById("tabBtn_" + key);
  if (activeTab) {
    activeTab.classList.add("is-active");
    activeTab.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
  }

  document.querySelectorAll(".comp-row").forEach((row) => {
    row.classList.remove("is-active");
  });
  const activeRow = document.getElementById("compRow_" + key);
  if (activeRow) {
    activeRow.classList.add("is-active");
  }

  const dossierView = document.getElementById("pathogenDossierView");
  if (dossierView) {
    dossierView.style.opacity = "0.4";
    setTimeout(() => {
      const mapping = [
        { id: "specimenImg", prop: "src", val: data.img },
        { id: "specSci", prop: "textContent", val: data.sci },
        { id: "specSeverity", prop: "textContent", val: data.severity },
        { id: "specGranularity", prop: "textContent", val: data.granularity },
        { id: "specFrac", prop: "textContent", val: data.fracCode },
        { id: "dossierNum", prop: "textContent", val: data.num },
        { id: "dossierTitle", prop: "textContent", val: data.title },
        { id: "dossierSci", prop: "textContent", val: data.sci },
        { id: "dossierShortDesc", prop: "textContent", val: data.shortDesc },
        { id: "dossierSymptoms", prop: "textContent", val: data.symptoms },
        { id: "dossierImpact", prop: "textContent", val: data.impact },
        { id: "dossierDeleafing", prop: "textContent", val: data.deleafing },
        { id: "dossierFrac", prop: "textContent", val: data.frac },
      ];
      mapping.forEach(({ id, prop, val }) => {
        const el = document.getElementById(id);
        if (el) el[prop] = val;
      });

      const newUrl = window.location.pathname + "?kelas=" + encodeURIComponent(key);
      window.history.replaceState({ kelas: key }, "", newUrl);

      dossierView.style.opacity = "1";

      if (scrollToTop) {
        dossierView.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }, 100);
  }
}

export function initPathogenCatalog() {
  if (!document.getElementById("pathogenDossierView")) return;
  const urlParams = new URLSearchParams(window.location.search);
  const requested = urlParams.get("kelas") || urlParams.get("penyakit") || "black-sigatoka";
  switchPathogen(requested);
}

export function bindCatalogGlobals() {
  window.switchPathogen = switchPathogen;
}
