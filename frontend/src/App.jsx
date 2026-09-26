import { useState, useEffect } from "react";
import {
  BookOpen,
  Check,
  FileDown,
  Loader2,
  Plus,
  RotateCcw,
  Save,
  Trash2,
  Upload,
  WandSparkles,
} from "lucide-react";
import "./index.css";

const LOCAL_API_BASE = "http://127.0.0.1:8000/api";
const PRODUCTION_API_BASE =
  "https://personal-cv-resume-maker-git-master-knanis-projects.vercel.app/api";
const API_BASE =
  import.meta.env.VITE_API_BASE ||
  (window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1"
    ? LOCAL_API_BASE
    : PRODUCTION_API_BASE);

const defaultData = {
  personal: {
    name: "",
    title: "",
    location: "",
    phone: "",
    email: "",
    github: "",
    linkedin: "",
  },
  profile: "",
  skills: { core: [], familiar: [], systems: [] },
  experience: [],
  projects: [],
  education: [],
  certifications: [],
  languages: [],
};

const demoData = {
  personal: {
    name: "Alex Morgan",
    title: "Full-Stack Developer",
    location: "Tunis, Tunisia",
    phone: "+216 20 000 000",
    email: "alex.morgan@example.com",
    github: "https://github.com/alexmorgan",
    linkedin: "https://linkedin.com/in/alexmorgan",
  },
  profile:
    "Creative developer who builds reliable web products with modern JavaScript, Python, and cloud-native tools. Comfortable turning ideas into polished, maintainable user experiences.",
  skills: {
    core: ["React", "JavaScript", "Python", "FastAPI", "PostgreSQL"],
    familiar: ["TypeScript", "Docker", "GitHub Actions", "Tailwind CSS"],
    systems: ["RESTful APIs", "Agile/Scrum", "Linux", "JWT Authentication"],
  },
  experience: [
    {
      position: "Full-Stack Developer",
      company: "Northstar Labs",
      location: "Remote",
      start_date: "2024",
      end_date: "Present",
      description: [
        "Built customer-facing React features and FastAPI services for a growing SaaS platform.",
        "Improved release reliability by introducing automated testing and containerized deployments.",
      ],
    },
  ],
  projects: [
    {
      name: "Orbit Task Manager",
      technologies: "React, FastAPI & PostgreSQL",
      description: [
        "Created a collaborative task manager with role-based access and activity history.",
      ],
    },
  ],
  education: [
    {
      degree: "B.Sc. Computer Science",
      institution: "Digital University",
      start_date: "2020",
      end_date: "2024",
    },
  ],
  certifications: [
    {
      name: "Cloud Fundamentals",
      institution: "Open Learning Institute",
      date: "2024",
    },
  ],
  languages: [
    { name: "English", level: "Professional" },
    { name: "French", level: "Professional" },
  ],
};

const cloneData = (value) => JSON.parse(JSON.stringify(value));

const defaultCoverLetter = {
  personal: {
    full_name: "",
    professional_title: "",
    address: "",
    city: "",
    country: "",
    phone: "",
    email: "",
    linkedin: "",
    github: "",
  },
  application: {
    job_title: "",
    company_name: "",
    company_address: "",
    hiring_manager_name: "",
    application_date: new Date().toISOString().slice(0, 10),
    reference: "",
  },
  content: {
    subject: "",
    salutation: "Dear Hiring Manager,",
    opening: "",
    body_paragraphs: [],
    closing: "Thank you for considering my application.",
    typed_name: "",
  },
  source_cv: { profile: "", skills: [], experience: [], education: [] },
  signature: {
    enabled: false,
    signature_id: null,
    alignment: "left",
    width_mm: 38,
    vertical_spacing_mm: 2,
  },
  template: { name: "classic", font_family: "Helvetica" },
};

function App() {
  const [data, setData] = useState(() => cloneData(demoData));
  const [activeTab, setActiveTab] = useState("Personal");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [library, setLibrary] = useState([]);
  const [libraryName, setLibraryName] = useState("");
  const [libraryLoading, setLibraryLoading] = useState(false);
  const [importing, setImporting] = useState(false);
  const [driveFiles, setDriveFiles] = useState([]);
  const [driveStatus, setDriveStatus] = useState({
    configured: false,
    connected: false,
  });
  const [driveLoading, setDriveLoading] = useState(false);
  const [coverLetter, setCoverLetter] = useState(() =>
    cloneData(defaultCoverLetter),
  );
  const [coverTab, setCoverTab] = useState("Details");
  const [signature, setSignature] = useState(null);
  const [signatureLoading, setSignatureLoading] = useState(false);
  const [coverGenerating, setCoverGenerating] = useState(false);
  const [skillDrafts, setSkillDrafts] = useState({
    core: "",
    familiar: "",
    systems: "",
  });

  const clearSkillCategory = (category) => {
    if (!data.skills[category]?.length && !skillDrafts[category]) return;
    if (!window.confirm(`Clear all ${category} skills?`)) return;
    setData((previous) => ({
      ...previous,
      skills: { ...previous.skills, [category]: [] },
    }));
    setSkillDrafts((previous) => ({ ...previous, [category]: "" }));
  };

  const mergeData = (fetched) => ({
    ...defaultData,
    ...fetched,
    personal: { ...defaultData.personal, ...(fetched.personal || {}) },
    skills: { ...defaultData.skills, ...(fetched.skills || {}) },
  });

  useEffect(() => {
    fetch(`${API_BASE}/cv`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((fetched) => {
        setData(mergeData(fetched));
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error loading CV data:", err);
        setLoading(false);
      });

    loadLibrary();
    loadDriveStatus();
  }, []);

  const loadDriveStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/google-drive/status`);
      if (!res.ok) return;
      const status = await res.json();
      setDriveStatus(status);
      if (status.connected) loadDriveFiles();
    } catch (err) {
      console.error("Error checking Google Drive:", err);
    }
  };

  const loadDriveFiles = async () => {
    try {
      const res = await fetch(`${API_BASE}/google-drive/files`);
      if (!res.ok) return;
      setDriveFiles(await res.json());
    } catch (err) {
      console.error("Error loading Google Drive files:", err);
    }
  };

  const connectGoogleDrive = () => {
    window.location.href = `${API_BASE}/google-drive/connect`;
  };

  const saveToGoogleDrive = async () => {
    setDriveLoading(true);
    try {
      const res = await fetch(`${API_BASE}/google-drive/files`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: libraryName.trim() || "CV Studio - Current.json",
          data,
        }),
      });
      const result = await res.json().catch(() => ({}));
      if (!res.ok)
        throw new Error(result.detail || "Failed to save to Google Drive");
      setLibraryName("");
      await loadDriveFiles();
      alert(`Saved ${result.name} to Google Drive.`);
    } catch (err) {
      alert("Error saving to Google Drive: " + err.message);
    } finally {
      setDriveLoading(false);
    }
  };

  const loadFromGoogleDrive = async (file) => {
    setDriveLoading(true);
    try {
      const res = await fetch(`${API_BASE}/google-drive/files/${file.id}`);
      const result = await res.json().catch(() => ({}));
      if (!res.ok)
        throw new Error(result.detail || "Failed to load from Google Drive");
      setData(mergeData(result.data));
      setActiveTab("Personal");
      alert(`Loaded “${file.name}” from Google Drive.`);
    } catch (err) {
      alert("Error loading from Google Drive: " + err.message);
    } finally {
      setDriveLoading(false);
    }
  };

  const loadLibrary = async () => {
    try {
      const res = await fetch(`${API_BASE}/library`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setLibrary(await res.json());
    } catch (err) {
      console.error("Error loading CV library:", err);
    }
  };

  const resetSection = (section) => {
    const labels = {
      personal: "personal details",
      profile: "professional summary",
      skills: "skills",
      experience: "experience",
      projects: "projects",
      education: "education",
      other: "certifications and languages",
    };
    if (!window.confirm(`Clear all ${labels[section]}?`)) return;
    const emptySections = {
      personal: { ...defaultData.personal },
      profile: "",
      skills: { ...defaultData.skills },
      experience: [],
      projects: [],
      education: [],
      other: { certifications: [], languages: [] },
    };
    setData((prev) => ({
      ...prev,
      ...(section === "other"
        ? emptySections.other
        : { [section]: emptySections[section] }),
    }));
  };

  const handleSaveToLibrary = async () => {
    const name = libraryName.trim() || `CV ${new Date().toLocaleString()}`;
    setLibraryLoading(true);
    try {
      const res = await fetch(`${API_BASE}/library`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, data }),
      });
      if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        throw new Error(error.detail || "Failed to save CV to library");
      }
      setLibraryName("");
      await loadLibrary();
      alert("CV saved to library!");
    } catch (err) {
      alert("Error saving to library: " + err.message);
    } finally {
      setLibraryLoading(false);
    }
  };

  const handleImportPdf = async (event) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;

    setImporting(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${API_BASE}/import-pdf`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        throw new Error(error.detail || "Failed to import PDF");
      }
      const result = await res.json();
      setData(mergeData(result.data));
      setActiveTab("Personal");
      alert(`Imported ${result.filename}. Please review the extracted fields.`);
    } catch (err) {
      alert("Error importing PDF: " + err.message);
    } finally {
      setImporting(false);
    }
  };

  const loadLibraryItem = (item) => {
    setData(mergeData(item.data));
    setActiveTab("Personal");
    alert(`Loaded “${item.name}”`);
  };

  const deleteLibraryItem = async (item) => {
    if (!window.confirm(`Delete “${item.name}” from the library?`)) return;
    try {
      const res = await fetch(`${API_BASE}/library/${item.id}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Failed to delete library item");
      setLibrary((items) => items.filter((entry) => entry.id !== item.id));
    } catch (err) {
      alert("Error deleting library item: " + err.message);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch(`${API_BASE}/cv`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ data }),
      });
      if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        throw new Error(error.detail || "Failed to save");
      }
      alert("Saved successfully!");
    } catch (err) {
      alert("Error saving: " + err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const res = await fetch(`${API_BASE}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ data }),
      });
      if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        throw new Error(error.detail || "Failed to generate PDF");
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "cv.pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert("Error generating PDF: " + err.message);
    } finally {
      setGenerating(false);
    }
  };

  const updateCover = (path, value) => {
    setCoverLetter((previous) => {
      const next = cloneData(previous);
      let current = next;
      path.slice(0, -1).forEach((key) => {
        current = current[key];
      });
      current[path[path.length - 1]] = value;
      return next;
    });
  };

  const reuseCvData = () => {
    setCoverLetter((previous) => ({
      ...previous,
      personal: {
        ...previous.personal,
        full_name: data.personal.name,
        professional_title: data.personal.title,
        city: data.personal.location,
        phone: data.personal.phone,
        email: data.personal.email,
        linkedin: data.personal.linkedin,
        github: data.personal.github,
      },
      content: { ...previous.content, typed_name: data.personal.name },
      source_cv: {
        profile: data.profile,
        skills: Object.values(data.skills).flat(),
        experience: data.experience,
        education: data.education,
      },
    }));
  };

  const handleCoverImport = async (event) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    setImporting(true);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${API_BASE}/cover-letters/import-pdf`, {
        method: "POST",
        body: form,
      });
      const result = await res.json();
      if (!res.ok)
        throw new Error(result.detail || "Could not import cover letter");
      setCoverLetter(result.data);
      setCoverTab("Details");
      alert("Cover letter imported. Please review the extracted fields.");
    } catch (err) {
      alert(err.message);
    } finally {
      setImporting(false);
    }
  };

  const handleSignature = async (event, mode) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    setSignatureLoading(true);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(
        `${API_BASE}/signatures/${mode === "template" ? "process-template" : "process-upload"}`,
        { method: "POST", body: form },
      );
      const result = await res.json();
      if (!res.ok)
        throw new Error(result.detail || "Could not process signature");
      setSignature(result);
      setCoverLetter((previous) => ({
        ...previous,
        signature: {
          ...previous.signature,
          signature_id: result.signature_id,
          enabled: true,
        },
      }));
      setCoverTab("Signature");
    } catch (err) {
      alert(err.message);
    } finally {
      setSignatureLoading(false);
    }
  };

  const generateCoverLetter = async () => {
    setCoverGenerating(true);
    try {
      const res = await fetch(`${API_BASE}/cover-letters/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ data: coverLetter }),
      });
      if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        throw new Error(error.detail || "Failed to generate cover letter");
      }
      const url = window.URL.createObjectURL(await res.blob());
      const link = document.createElement("a");
      link.href = url;
      link.download = "cover-letter.pdf";
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert(err.message);
    } finally {
      setCoverGenerating(false);
    }
  };

  const coverSteps = ["Details", "Content", "Signature"];
  const coverProgress = Math.round(
    ((coverSteps.indexOf(coverTab) + 1) / coverSteps.length) * 100,
  );

  const coverPreview = (
    <article className="letter-preview" aria-label="Cover letter preview">
      <div className="letter-preview-topline">
        {coverLetter.application.application_date || "Application date"}
      </div>
      <div className="letter-preview-sender">
        <strong>{coverLetter.personal.full_name || "Your name"}</strong>
        <span>
          {[
            coverLetter.personal.address,
            coverLetter.personal.city,
            coverLetter.personal.country,
          ]
            .filter(Boolean)
            .join(", ") || "Your address"}
        </span>
        <span>{coverLetter.personal.email || "your.email@example.com"}</span>
        <span>{coverLetter.personal.phone || "Your phone number"}</span>
      </div>
      <div className="letter-preview-recipient">
        <strong>
          {coverLetter.application.hiring_manager_name || "Hiring Manager"}
        </strong>
        <span>{coverLetter.application.company_name || "Company name"}</span>
        <span>
          {coverLetter.application.company_address || "Company address"}
        </span>
      </div>
      <h3>
        {coverLetter.content.subject || "Subject: Your application subject"}
      </h3>
      <p>{coverLetter.content.salutation || "Dear Hiring Manager,"}</p>
      <p>
        {coverLetter.content.opening ||
          "Your opening paragraph will appear here."}
      </p>
      {coverLetter.content.body_paragraphs.map((paragraph, index) => (
        <p key={`${paragraph}-${index}`}>{paragraph}</p>
      ))}
      <p>
        {coverLetter.content.closing ||
          "Thank you for considering my application."}
      </p>
      {coverLetter.signature.enabled && signature ? (
        <img
          className="letter-preview-signature"
          src={`${API_BASE.replace(/\/api$/, "")}${signature.preview_url}`}
          alt="Signature"
        />
      ) : (
        <div className="signature-placeholder">Signature optional</div>
      )}
      <strong>
        {coverLetter.content.typed_name ||
          coverLetter.personal.full_name ||
          "Your typed name"}
      </strong>
    </article>
  );

  const updateNested = (path, value) => {
    setData((prev) => {
      const newData = { ...prev };
      let current = newData;
      for (let i = 0; i < path.length - 1; i++) {
        current = current[path[i]];
      }
      current[path[path.length - 1]] = value;
      return newData;
    });
  };

  const addSkill = (category) => {
    const value = skillDrafts[category].trim();
    if (!value) return;

    setData((previous) => {
      const skills = previous.skills[category] || [];
      if (skills.some((skill) => skill.toLowerCase() === value.toLowerCase())) {
        return previous;
      }
      return {
        ...previous,
        skills: { ...previous.skills, [category]: [...skills, value] },
      };
    });
    setSkillDrafts((previous) => ({ ...previous, [category]: "" }));
  };

  const removeSkill = (category, index) => {
    setData((previous) => ({
      ...previous,
      skills: {
        ...previous.skills,
        [category]: previous.skills[category].filter(
          (_, itemIndex) => itemIndex !== index,
        ),
      },
    }));
  };

  const addArrayItem = (path, emptyItem) => {
    setData((prev) => {
      const newData = { ...prev };
      let current = newData;
      for (let i = 0; i < path.length - 1; i++) {
        current = current[path[i]];
      }
      current[path[path.length - 1]] = [
        ...current[path[path.length - 1]],
        emptyItem,
      ];
      return newData;
    });
  };

  const removeArrayItem = (path, index) => {
    setData((prev) => {
      const newData = { ...prev };
      let current = newData;
      for (let i = 0; i < path.length - 1; i++) {
        current = current[path[i]];
      }
      const arr = [...current[path[path.length - 1]]];
      arr.splice(index, 1);
      current[path[path.length - 1]] = arr;
      return newData;
    });
  };

  if (loading)
    return (
      <div
        className="container"
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
        }}
      >
        <Loader2
          className="animate-spin"
          size={48}
          color="var(--accent-primary)"
        />
      </div>
    );

  const tabs = [
    "Cover Letter",
    "Personal",
    "Profile",
    "Skills",
    "Experience",
    "Projects",
    "Education",
    "Other",
    "Library",
  ];

  return (
    <div className="container">
      <div className="header">
        <h1>CV Studio</h1>
        <div className="flex gap-4 header-actions">
          <button className="secondary" onClick={handleSave} disabled={saving}>
            {saving ? (
              <Loader2 className="animate-spin" size={18} />
            ) : (
              <Save size={18} />
            )}
            Save Data
          </button>
          <button onClick={handleGenerate} disabled={generating}>
            {generating ? (
              <Loader2 className="animate-spin" size={18} />
            ) : (
              <FileDown size={18} />
            )}
            Generate PDF
          </button>
        </div>
      </div>

      <div className="tabs">
        {tabs.map((t) => (
          <button
            key={t}
            className={`tab ${activeTab === t ? "active" : ""}`}
            onClick={() => setActiveTab(t)}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="glass-panel editor-panel">
        {activeTab === "Cover Letter" && (
          <div>
            <div className="cover-hero">
              <div>
                <span className="eyebrow">
                  <WandSparkles size={15} /> DOCUMENT WORKSPACE
                </span>
                <h2 className="cover-title">
                  Build a letter that opens doors.
                </h2>
                <p className="muted">
                  Create, import, sign, and download a polished searchable PDF.
                </p>
              </div>
              <div className="cover-hero-actions">
                <button className="secondary" onClick={reuseCvData}>
                  <Check size={16} />
                  Use information from my CV
                </button>
                <label className="button secondary">
                  {importing ? "Importing..." : "Import PDF"}
                  <input
                    hidden
                    type="file"
                    accept="application/pdf,.pdf"
                    onChange={handleCoverImport}
                  />
                </label>
                <button
                  onClick={generateCoverLetter}
                  disabled={coverGenerating}
                >
                  <FileDown size={17} />{" "}
                  {coverGenerating ? "Generating..." : "Generate PDF"}
                </button>
              </div>
            </div>
            <div className="cover-progress" aria-label="Cover letter progress">
              <div className="progress-heading">
                <span>Cover letter setup</span>
                <strong>{coverProgress}% complete</strong>
              </div>
              <div className="progress-track">
                <span style={{ width: `${coverProgress}%` }} />
              </div>
              <div className="cover-step-list">
                {coverSteps.map((tab, index) => (
                  <button
                    key={tab}
                    className={`cover-step ${coverTab === tab ? "active" : ""} ${index < coverSteps.indexOf(coverTab) ? "complete" : ""}`}
                    onClick={() => setCoverTab(tab)}
                  >
                    <span>
                      {index < coverSteps.indexOf(coverTab) ? (
                        <Check size={15} />
                      ) : (
                        index + 1
                      )}
                    </span>
                    {tab}
                  </button>
                ))}
              </div>
            </div>
            <div className="cover-workspace">
              <div className="cover-form-column">
                {coverTab === "Details" && (
                  <div className="grid grid-cols-2">
                    {Object.entries(coverLetter.personal).map(
                      ([field, value]) => (
                        <div className="form-group" key={field}>
                          <label>{field.replaceAll("_", " ")}</label>
                          <input
                            value={value}
                            onChange={(e) =>
                              updateCover(["personal", field], e.target.value)
                            }
                          />
                        </div>
                      ),
                    )}
                    {Object.entries(coverLetter.application).map(
                      ([field, value]) => (
                        <div className="form-group" key={field}>
                          <label>{field.replaceAll("_", " ")}</label>
                          <input
                            value={value}
                            onChange={(e) =>
                              updateCover(
                                ["application", field],
                                e.target.value,
                              )
                            }
                          />
                        </div>
                      ),
                    )}
                  </div>
                )}
                {coverTab === "Content" && (
                  <div>
                    {[
                      ["subject", "Subject"],
                      ["salutation", "Salutation"],
                      ["opening", "Opening paragraph"],
                      ["closing", "Closing"],
                      ["typed_name", "Typed name"],
                    ].map(([field, label]) => (
                      <div className="form-group" key={field}>
                        <label>{label}</label>
                        <textarea
                          rows={field === "opening" ? 5 : 2}
                          value={coverLetter.content[field]}
                          onChange={(e) =>
                            updateCover(["content", field], e.target.value)
                          }
                        />
                      </div>
                    ))}
                    <div className="form-group">
                      <label>Body paragraphs (one paragraph per line)</label>
                      <textarea
                        rows={8}
                        value={coverLetter.content.body_paragraphs.join("\n\n")}
                        onChange={(e) =>
                          updateCover(
                            ["content", "body_paragraphs"],
                            e.target.value.split(/\n\s*\n/).filter(Boolean),
                          )
                        }
                      />
                    </div>
                  </div>
                )}
                {coverTab === "Signature" && (
                  <div>
                    <p className="muted">
                      Upload a clear PNG/JPG signature, or download and scan the
                      printable template.
                    </p>
                    <div className="flex gap-2">
                      <label className="button">
                        {signatureLoading
                          ? "Processing..."
                          : "Upload Signature"}
                        <input
                          hidden
                          type="file"
                          accept="image/png,image/jpeg"
                          onChange={(e) => handleSignature(e, "upload")}
                        />
                      </label>
                      <a
                        className="button secondary"
                        href={`${API_BASE}/signatures/template`}
                        download
                      >
                        Download Template
                      </a>
                      <label className="button secondary">
                        Scan Template
                        <input
                          hidden
                          type="file"
                          accept="image/png,image/jpeg"
                          onChange={(e) => handleSignature(e, "template")}
                        />
                      </label>
                    </div>
                    {signature && (
                      <div className="signature-review">
                        <img
                          src={`${API_BASE.replace(/\/api$/, "")}${signature.preview_url}`}
                          alt="Processed handwritten signature preview"
                        />
                        <p className="muted">
                          {signature.confidence >= 0.85
                            ? "Signature detected successfully."
                            : "Signature extracted. Please verify the preview."}
                        </p>
                        <div className="grid grid-cols-2">
                          <div className="form-group">
                            <label>Width (mm)</label>
                            <input
                              type="number"
                              min="20"
                              max="60"
                              value={coverLetter.signature.width_mm}
                              onChange={(e) =>
                                updateCover(
                                  ["signature", "width_mm"],
                                  Number(e.target.value),
                                )
                              }
                            />
                          </div>
                          <div className="form-group">
                            <label>Alignment</label>
                            <select
                              value={coverLetter.signature.alignment}
                              onChange={(e) =>
                                updateCover(
                                  ["signature", "alignment"],
                                  e.target.value,
                                )
                              }
                            >
                              <option value="left">Left</option>
                              <option value="center">Center</option>
                              <option value="right">Right</option>
                            </select>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
                <div className="cover-footer-actions">
                  <button
                    className="secondary"
                    disabled={coverSteps.indexOf(coverTab) === 0}
                    onClick={() =>
                      setCoverTab(
                        coverSteps[
                          Math.max(0, coverSteps.indexOf(coverTab) - 1)
                        ],
                      )
                    }
                  >
                    Back
                  </button>
                  {coverTab !== "Signature" ? (
                    <button
                      onClick={() =>
                        setCoverTab(
                          coverSteps[coverSteps.indexOf(coverTab) + 1],
                        )
                      }
                    >
                      Continue
                    </button>
                  ) : (
                    <button
                      onClick={generateCoverLetter}
                      disabled={coverGenerating}
                    >
                      <FileDown size={17} /> Download PDF
                    </button>
                  )}
                </div>
              </div>
              <aside className="cover-preview-column">
                <div className="preview-heading">
                  <div>
                    <span className="eyebrow">LIVE PREVIEW</span>
                    <h3>Letter preview</h3>
                  </div>
                  <select
                    value={coverLetter.template.name}
                    onChange={(e) =>
                      updateCover(["template", "name"], e.target.value)
                    }
                    aria-label="Cover letter template"
                  >
                    <option value="classic">Classic</option>
                    <option value="modern">Modern</option>
                    <option value="minimal">Minimal</option>
                    <option value="ats">ATS</option>
                  </select>
                </div>
                {coverPreview}
              </aside>
            </div>
          </div>
        )}
        {activeTab === "Library" && (
          <div>
            <div className="library-header">
              <div>
                <h2 className="section-title" style={{ margin: 0 }}>
                  <BookOpen size={22} /> CV Library
                </h2>
                <p className="muted">
                  Save versions of your CV and return to them whenever you need.
                </p>
              </div>
              <div className="library-actions">
                <button
                  className="secondary"
                  onClick={() => setData(cloneData(demoData))}
                >
                  Load Demo CV
                </button>
                <label className="button secondary">
                  {importing ? (
                    <Loader2 className="animate-spin" size={18} />
                  ) : (
                    <Upload size={18} />
                  )}
                  Load from PDF
                  <input
                    type="file"
                    accept="application/pdf,.pdf"
                    onChange={handleImportPdf}
                    disabled={importing}
                    hidden
                  />
                </label>
              </div>
            </div>
            <div className="library-save-panel">
              <div>
                <strong>Save current version</strong>
                <p className="muted">
                  Give this CV a name so you can find it later.
                </p>
              </div>
              <div className="library-save flex gap-2">
                <input
                  value={libraryName}
                  placeholder="Version name, e.g. Backend CV"
                  onChange={(e) => setLibraryName(e.target.value)}
                />
                <button onClick={handleSaveToLibrary} disabled={libraryLoading}>
                  {libraryLoading ? (
                    <Loader2 className="animate-spin" size={18} />
                  ) : (
                    <Save size={18} />
                  )}
                  Save Version
                </button>
              </div>
            </div>
            <div className="library-save-panel">
              <div>
                <strong>Google Drive</strong>
                <p className="muted">
                  {driveStatus.connected
                    ? "Your CV versions can be saved privately in Google Drive."
                    : "Connect Google Drive to keep CV versions in the cloud."}
                </p>
              </div>
              {!driveStatus.connected ? (
                <button
                  className="secondary"
                  onClick={connectGoogleDrive}
                  disabled={!driveStatus.configured}
                >
                  Connect Google Drive
                </button>
              ) : (
                <button onClick={saveToGoogleDrive} disabled={driveLoading}>
                  {driveLoading ? (
                    <Loader2 className="animate-spin" size={18} />
                  ) : (
                    <Save size={18} />
                  )}
                  Save to Drive
                </button>
              )}
            </div>
            {driveStatus.connected && driveFiles.length > 0 && (
              <div className="library-list">
                <h3>Google Drive versions</h3>
                {driveFiles.map((file) => (
                  <div className="library-item glass-panel" key={file.id}>
                    <div>
                      <strong>{file.name}</strong>
                      <div className="muted">
                        {new Date(file.modifiedTime).toLocaleString()}
                      </div>
                    </div>
                    <button
                      className="secondary"
                      onClick={() => loadFromGoogleDrive(file)}
                      disabled={driveLoading}
                    >
                      Load
                    </button>
                  </div>
                ))}
              </div>
            )}
            {library.length === 0 ? (
              <div className="empty-state">No saved CV versions yet.</div>
            ) : (
              <div className="library-list">
                {library.map((item) => (
                  <div className="library-item glass-panel" key={item.id}>
                    <div>
                      <strong>{item.name}</strong>
                      <div className="muted">
                        {new Date(item.created_at).toLocaleString()}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        className="secondary"
                        onClick={() => loadLibraryItem(item)}
                      >
                        Load
                      </button>
                      <button
                        className="danger icon-only"
                        onClick={() => deleteLibraryItem(item)}
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "Personal" && (
          <div>
            <div className="section-toolbar">
              <h2 className="section-title" style={{ margin: 0 }}>
                Personal Details
              </h2>
              <button
                className="secondary"
                onClick={() => resetSection("personal")}
              >
                <RotateCcw size={16} /> Clear Section
              </button>
            </div>
            <div className="grid grid-cols-2">
              {Object.keys(defaultData.personal).map((field) => (
                <div className="form-group" key={field}>
                  <label style={{ textTransform: "capitalize" }}>{field}</label>
                  <input
                    value={data.personal[field]}
                    onChange={(e) =>
                      updateNested(["personal", field], e.target.value)
                    }
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === "Profile" && (
          <div>
            <div className="section-toolbar">
              <h2 className="section-title" style={{ margin: 0 }}>
                Professional Summary
              </h2>
              <button
                className="secondary"
                onClick={() => resetSection("profile")}
              >
                <RotateCcw size={16} /> Clear Section
              </button>
            </div>
            <div className="form-group">
              <label>Professional Summary</label>
              <textarea
                rows={8}
                value={data.profile}
                onChange={(e) => updateNested(["profile"], e.target.value)}
              />
            </div>
          </div>
        )}

        {activeTab === "Skills" && (
          <div>
            <div className="section-toolbar">
              <h2 className="section-title" style={{ margin: 0 }}>
                Skills
              </h2>
              <button
                className="secondary"
                onClick={() => resetSection("skills")}
              >
                <RotateCcw size={16} /> Clear Section
              </button>
            </div>
            <div className="grid skills-editor-list">
              {["core", "familiar", "systems"].map((cat) => (
                <div className="skill-editor form-group" key={cat}>
                  <label style={{ textTransform: "capitalize" }}>
                    {cat} skills
                  </label>
                  <div className="skill-input-row">
                    <input
                      value={skillDrafts[cat]}
                      placeholder={`Add a ${cat} skill`}
                      onChange={(e) =>
                        setSkillDrafts((previous) => ({
                          ...previous,
                          [cat]: e.target.value,
                        }))
                      }
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          e.preventDefault();
                          addSkill(cat);
                        }
                      }}
                    />
                    <button
                      type="button"
                      className="skill-add-button"
                      aria-label={`Add ${cat} skill`}
                      onClick={() => addSkill(cat)}
                    >
                      <Plus size={17} />
                    </button>
                  </div>
                  <div className="skill-chips" aria-live="polite">
                    {(data.skills[cat] || []).map((skill, index) => (
                      <span className="skill-chip" key={`${skill}-${index}`}>
                        {skill}
                        <button
                          type="button"
                          aria-label={`Remove ${skill}`}
                          onClick={() => removeSkill(cat, index)}
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                  <button
                    type="button"
                    className="skill-clear-button"
                    aria-label={`Clear ${cat.charAt(0).toUpperCase() + cat.slice(1)} Skills`}
                    onClick={() => clearSkillCategory(cat)}
                  >
                    Clear {cat.charAt(0).toUpperCase() + cat.slice(1)} Skills
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === "Experience" && (
          <div>
            <div className="section-toolbar">
              <h2 className="section-title" style={{ margin: 0 }}>
                Work Experience
              </h2>
              <div className="flex gap-2">
                <button
                  className="secondary"
                  onClick={() => resetSection("experience")}
                >
                  <RotateCcw size={16} /> Clear
                </button>
                <button
                  className="secondary"
                  onClick={() =>
                    addArrayItem(["experience"], {
                      position: "",
                      company: "",
                      location: "",
                      start_date: "",
                      end_date: "",
                      description: [],
                    })
                  }
                >
                  <Plus size={18} /> Add Role
                </button>
              </div>
            </div>
            {data.experience.map((exp, idx) => (
              <div
                key={idx}
                className="card glass-panel"
                style={{ background: "rgba(255,255,255,0.02)" }}
              >
                <div className="card-actions">
                  <button
                    className="danger icon-only"
                    onClick={() => removeArrayItem(["experience"], idx)}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
                <div className="grid grid-cols-2">
                  <div className="form-group">
                    <label>Position</label>
                    <input
                      value={exp.position}
                      onChange={(e) =>
                        updateNested(
                          ["experience", idx, "position"],
                          e.target.value,
                        )
                      }
                    />
                  </div>
                  <div className="form-group">
                    <label>Company</label>
                    <input
                      value={exp.company}
                      onChange={(e) =>
                        updateNested(
                          ["experience", idx, "company"],
                          e.target.value,
                        )
                      }
                    />
                  </div>
                  <div className="form-group">
                    <label>Location</label>
                    <input
                      value={exp.location}
                      onChange={(e) =>
                        updateNested(
                          ["experience", idx, "location"],
                          e.target.value,
                        )
                      }
                    />
                  </div>
                  <div className="flex gap-2">
                    <div className="form-group" style={{ flex: 1 }}>
                      <label>Start Date</label>
                      <input
                        value={exp.start_date}
                        onChange={(e) =>
                          updateNested(
                            ["experience", idx, "start_date"],
                            e.target.value,
                          )
                        }
                      />
                    </div>
                    <div className="form-group" style={{ flex: 1 }}>
                      <label>End Date</label>
                      <input
                        value={exp.end_date}
                        onChange={(e) =>
                          updateNested(
                            ["experience", idx, "end_date"],
                            e.target.value,
                          )
                        }
                      />
                    </div>
                  </div>
                </div>
                <div className="form-group">
                  <label>Description (bullet points, one per line)</label>
                  <textarea
                    rows={5}
                    value={exp.description?.join("\n") || ""}
                    onChange={(e) =>
                      updateNested(
                        ["experience", idx, "description"],
                        e.target.value.split("\n"),
                      )
                    }
                  />
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === "Projects" && (
          <div>
            <div className="section-toolbar">
              <h2 className="section-title" style={{ margin: 0 }}>
                Projects
              </h2>
              <div className="flex gap-2">
                <button
                  className="secondary"
                  onClick={() => resetSection("projects")}
                >
                  <RotateCcw size={16} /> Clear
                </button>
                <button
                  className="secondary"
                  onClick={() =>
                    addArrayItem(["projects"], {
                      name: "",
                      technologies: "",
                      description: [],
                    })
                  }
                >
                  <Plus size={18} /> Add Project
                </button>
              </div>
            </div>
            {data.projects.map((proj, idx) => (
              <div
                key={idx}
                className="card glass-panel"
                style={{ background: "rgba(255,255,255,0.02)" }}
              >
                <div className="card-actions">
                  <button
                    className="danger icon-only"
                    onClick={() => removeArrayItem(["projects"], idx)}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
                <div className="grid grid-cols-2">
                  <div className="form-group">
                    <label>Project Name</label>
                    <input
                      value={proj.name}
                      onChange={(e) =>
                        updateNested(["projects", idx, "name"], e.target.value)
                      }
                    />
                  </div>
                  <div className="form-group">
                    <label>Technologies</label>
                    <input
                      value={proj.technologies}
                      onChange={(e) =>
                        updateNested(
                          ["projects", idx, "technologies"],
                          e.target.value,
                        )
                      }
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label>Description (bullet points, one per line)</label>
                  <textarea
                    rows={4}
                    value={proj.description?.join("\n") || ""}
                    onChange={(e) =>
                      updateNested(
                        ["projects", idx, "description"],
                        e.target.value.split("\n"),
                      )
                    }
                  />
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === "Education" && (
          <div>
            <div className="section-toolbar">
              <h2 className="section-title" style={{ margin: 0 }}>
                Education
              </h2>
              <div className="flex gap-2">
                <button
                  className="secondary"
                  onClick={() => resetSection("education")}
                >
                  <RotateCcw size={16} /> Clear
                </button>
                <button
                  className="secondary"
                  onClick={() =>
                    addArrayItem(["education"], {
                      degree: "",
                      institution: "",
                      start_date: "",
                      end_date: "",
                    })
                  }
                >
                  <Plus size={18} /> Add Education
                </button>
              </div>
            </div>
            {data.education.map((edu, idx) => (
              <div
                key={idx}
                className="card glass-panel"
                style={{ background: "rgba(255,255,255,0.02)" }}
              >
                <div className="card-actions">
                  <button
                    className="danger icon-only"
                    onClick={() => removeArrayItem(["education"], idx)}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
                <div className="grid grid-cols-2">
                  <div className="form-group">
                    <label>Degree</label>
                    <input
                      value={edu.degree}
                      onChange={(e) =>
                        updateNested(
                          ["education", idx, "degree"],
                          e.target.value,
                        )
                      }
                    />
                  </div>
                  <div className="form-group">
                    <label>Institution</label>
                    <input
                      value={edu.institution}
                      onChange={(e) =>
                        updateNested(
                          ["education", idx, "institution"],
                          e.target.value,
                        )
                      }
                    />
                  </div>
                  <div className="form-group">
                    <label>Start Date</label>
                    <input
                      value={edu.start_date}
                      onChange={(e) =>
                        updateNested(
                          ["education", idx, "start_date"],
                          e.target.value,
                        )
                      }
                    />
                  </div>
                  <div className="form-group">
                    <label>End Date</label>
                    <input
                      value={edu.end_date}
                      onChange={(e) =>
                        updateNested(
                          ["education", idx, "end_date"],
                          e.target.value,
                        )
                      }
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === "Other" && (
          <div>
            <div className="section-toolbar section-toolbar-end">
              <button
                className="secondary"
                onClick={() => resetSection("other")}
              >
                <RotateCcw size={16} /> Clear Other Sections
              </button>
            </div>
            <div className="grid grid-cols-2">
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h2 className="section-title" style={{ margin: 0 }}>
                    Certifications
                  </h2>
                  <button
                    className="secondary"
                    onClick={() =>
                      addArrayItem(["certifications"], {
                        name: "",
                        institution: "",
                        date: "",
                      })
                    }
                  >
                    <Plus size={18} />
                  </button>
                </div>
                {data.certifications.map((cert, idx) => (
                  <div
                    key={idx}
                    className="card glass-panel"
                    style={{ background: "rgba(255,255,255,0.02)" }}
                  >
                    <button
                      className="danger icon-only card-delete"
                      onClick={() => removeArrayItem(["certifications"], idx)}
                    >
                      <Trash2 size={12} />
                    </button>
                    <div className="form-group">
                      <label>Name</label>
                      <input
                        value={cert.name}
                        onChange={(e) =>
                          updateNested(
                            ["certifications", idx, "name"],
                            e.target.value,
                          )
                        }
                      />
                    </div>
                    <div className="form-group">
                      <label>Institution</label>
                      <input
                        value={cert.institution}
                        onChange={(e) =>
                          updateNested(
                            ["certifications", idx, "institution"],
                            e.target.value,
                          )
                        }
                      />
                    </div>
                    <div className="form-group">
                      <label>Date</label>
                      <input
                        value={cert.date}
                        onChange={(e) =>
                          updateNested(
                            ["certifications", idx, "date"],
                            e.target.value,
                          )
                        }
                      />
                    </div>
                  </div>
                ))}
              </div>

              <div>
                <div className="flex justify-between items-center mb-4">
                  <h2 className="section-title" style={{ margin: 0 }}>
                    Languages
                  </h2>
                  <button
                    className="secondary"
                    onClick={() =>
                      addArrayItem(["languages"], { name: "", level: "" })
                    }
                  >
                    <Plus size={18} />
                  </button>
                </div>
                {data.languages.map((lang, idx) => (
                  <div
                    key={idx}
                    className="card glass-panel"
                    style={{ background: "rgba(255,255,255,0.02)" }}
                  >
                    <button
                      className="danger icon-only card-delete"
                      onClick={() => removeArrayItem(["languages"], idx)}
                    >
                      <Trash2 size={12} />
                    </button>
                    <div className="form-group">
                      <label>Language</label>
                      <input
                        value={lang.name}
                        onChange={(e) =>
                          updateNested(
                            ["languages", idx, "name"],
                            e.target.value,
                          )
                        }
                      />
                    </div>
                    <div className="form-group">
                      <label>Level</label>
                      <input
                        value={lang.level}
                        onChange={(e) =>
                          updateNested(
                            ["languages", idx, "level"],
                            e.target.value,
                          )
                        }
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
