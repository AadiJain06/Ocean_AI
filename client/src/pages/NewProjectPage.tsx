import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";
import type { DocType } from "../types";

type SectionInput = { title: string; position: number };

export function NewProjectPage() {
  const navigate = useNavigate();
  const [docType, setDocType] = useState<DocType>("docx");
  const [title, setTitle] = useState("");
  const [topic, setTopic] = useState("");
  const [sections, setSections] = useState<SectionInput[]>([
    { title: "Overview", position: 1 },
    { title: "Insights", position: 2 },
    { title: "Next steps", position: 3 },
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateSection = (index: number, title: string) => {
    setSections((prev) =>
      prev.map((item, idx) => (idx === index ? { ...item, title } : item)).map((item, idx) => ({
        ...item,
        position: idx + 1,
      }))
    );
  };

  const addSection = () => {
    setSections((prev) => [...prev, { title: "New section", position: prev.length + 1 }]);
  };

  const removeSection = (index: number) => {
    setSections((prev) =>
      prev.filter((_, idx) => idx !== index).map((item, idx) => ({
        ...item,
        position: idx + 1,
      }))
    );
  };

  const suggestOutline = async () => {
    try {
      setError(null);
      const { data } = await api.post("/templates/outline", {
        topic,
        doc_type: docType,
        item_count: sections.length,
      });
      setSections(data.titles.map((title: string, idx: number) => ({ title, position: idx + 1 })));
    } catch (err: any) {
      setError(err.response?.data?.detail || "Unable to fetch template");
    }
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.post("/projects/", {
        title,
        topic,
        doc_type: docType,
        sections,
      });
      navigate(`/projects/${data.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Could not create project");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page narrow">
      <h1>New project</h1>
      <p>Pick a format, define structure, and start generating.</p>
      <form className="wizard" onSubmit={handleSubmit}>
        <label>Format</label>
        <div className="pill-group">
          <button
            type="button"
            className={docType === "docx" ? "pill active" : "pill"}
            onClick={() => setDocType("docx")}
          >
            Word
          </button>
          <button
            type="button"
            className={docType === "pptx" ? "pill active" : "pill"}
            onClick={() => setDocType("pptx")}
          >
            PowerPoint
          </button>
        </div>
        <label>Project title</label>
        <input value={title} onChange={(e) => setTitle(e.target.value)} required />
        <label>Main topic</label>
        <input value={topic} onChange={(e) => setTopic(e.target.value)} required />
        <div className="sections-head">
          <p>{docType === "docx" ? "Sections" : "Slides"}</p>
          <div className="head-actions">
            <button type="button" className="ghost" onClick={addSection}>
              Add
            </button>
            <button type="button" className="ghost" onClick={suggestOutline} disabled={!topic}>
              AI suggest outline
            </button>
          </div>
        </div>
        {sections.map((section, index) => (
          <div key={section.position} className="section-row">
            <input value={section.title} onChange={(e) => updateSection(index, e.target.value)} required />
            <button type="button" className="ghost" onClick={() => removeSection(index)} disabled={sections.length <= 1}>
              Remove
            </button>
          </div>
        ))}
        {error && <div className="error">{error}</div>}
        <button type="submit" disabled={loading}>
          {loading ? "Creating..." : "Create project"}
        </button>
      </form>
    </div>
  );
}

