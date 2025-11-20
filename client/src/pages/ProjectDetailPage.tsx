import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api/client";
import type { ProjectDetail, Section } from "../types";

type InputMaps = Record<number, string>;

export function ProjectDetailPage() {
  const { id } = useParams();
  const projectId = Number(id);
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [promptInputs, setPromptInputs] = useState<InputMaps>({});
  const [commentInputs, setCommentInputs] = useState<InputMaps>({});
  const [busySection, setBusySection] = useState<number | null>(null);
  const [globalBusy, setGlobalBusy] = useState(false);

  const loadProject = async () => {
    try {
      setError(null);
      const { data } = await api.get<ProjectDetail>(`/projects/${projectId}`);
      setProject(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Project not found");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!Number.isNaN(projectId)) {
      loadProject();
    }
  }, [projectId]);

  const handleGenerate = async (regenerate: boolean) => {
    setGlobalBusy(true);
    try {
      const { data } = await api.post<ProjectDetail>(`/projects/${projectId}/generate`, { regenerate });
      setProject(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Generation failed");
    } finally {
      setGlobalBusy(false);
    }
  };

  const handleRefine = async (section: Section) => {
    const prompt = promptInputs[section.id]?.trim();
    if (!prompt || prompt.length < 1) {
      setError("Please enter a refinement prompt");
      return;
    }
    setBusySection(section.id);
    setError(null);
    try {
      const { data } = await api.post<Section>(`/sections/${section.id}/refine`, { prompt: prompt.trim() });
      updateSection(data);
      setPromptInputs((prev) => ({ ...prev, [section.id]: "" }));
    } catch (err: any) {
      let errorMsg = "Could not refine section";
      if (err.response?.data?.detail) {
        if (Array.isArray(err.response.data.detail)) {
          errorMsg = err.response.data.detail.map((d: any) => d.msg || d).join(", ");
        } else {
          errorMsg = err.response.data.detail;
        }
      }
      setError(errorMsg);
    } finally {
      setBusySection(null);
    }
  };

  const handleFeedback = async (section: Section, value: "like" | "dislike") => {
    setBusySection(section.id);
    try {
      const { data } = await api.post<Section>(`/sections/${section.id}/feedback`, { value });
      updateSection(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Could not save feedback");
    } finally {
      setBusySection(null);
    }
  };

  const handleComment = async (section: Section) => {
    const comment = commentInputs[section.id]?.trim();
    if (!comment || comment.length < 2) {
      setError("Comment must be at least 2 characters");
      return;
    }
    setBusySection(section.id);
    setError(null);
    try {
      const { data } = await api.post<Section>(`/sections/${section.id}/comment`, { comment: comment.trim() });
      updateSection(data);
      setCommentInputs((prev) => ({ ...prev, [section.id]: "" }));
    } catch (err: any) {
      let errorMsg = "Could not save comment";
      if (err.response?.data?.detail) {
        if (Array.isArray(err.response.data.detail)) {
          errorMsg = err.response.data.detail.map((d: any) => d.msg || d).join(", ");
        } else {
          errorMsg = err.response.data.detail;
        }
      }
      setError(errorMsg);
    } finally {
      setBusySection(null);
    }
  };

  const handleExport = async (format: "docx" | "pptx") => {
    if (!project) return;
    setGlobalBusy(true);
    try {
      const response = await api.get(`/export/${project.id}`, {
        params: { format },
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `${project.title}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Export failed");
    } finally {
      setGlobalBusy(false);
    }
  };

  const updateSection = (updated: Section) => {
    setProject((prev) =>
      prev
        ? {
            ...prev,
            sections: prev.sections.map((section) => (section.id === updated.id ? updated : section)),
          }
        : prev
    );
  };

  if (loading) {
    return <p className="page">Loading...</p>;
  }

  if (!project) {
    return <p className="page">Project unavailable.</p>;
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>{project.title}</h1>
          <p>{project.topic}</p>
          <div className="tag-row">
            <span className="tag">{project.doc_type.toUpperCase()}</span>
            <span className={`status ${project.status}`}>{project.status}</span>
          </div>
        </div>
        <div className="head-actions">
          <button onClick={() => handleGenerate(false)} disabled={globalBusy}>
            Generate
          </button>
          <button onClick={() => handleGenerate(true)} disabled={globalBusy}>
            Regenerate
          </button>
          <button onClick={() => handleExport("docx")} disabled={globalBusy}>
            Export Word
          </button>
          <button onClick={() => handleExport("pptx")} disabled={globalBusy}>
            Export PowerPoint
          </button>
        </div>
      </div>
      {error && <div className="error">{error}</div>}
      <div className="section-grid">
        {project.sections.map((section) => (
          <div key={section.id} className="section-card">
            <div className="section-head">
              <h3>
                {section.position}. {section.title}
              </h3>
              <div className="tag-row">
                <button
                  className={section.feedback === "like" ? "pill active" : "pill"}
                  onClick={() => handleFeedback(section, "like")}
                  disabled={busySection === section.id}
                >
                  Like
                </button>
                <button
                  className={section.feedback === "dislike" ? "pill active" : "pill"}
                  onClick={() => handleFeedback(section, "dislike")}
                  disabled={busySection === section.id}
                >
                  Dislike
                </button>
              </div>
            </div>
            <p className="section-content">{section.content || "No content yet."}</p>
            <div className="refine-block">
              <label>Refinement prompt</label>
              <textarea
                value={promptInputs[section.id] || ""}
                onChange={(e) => setPromptInputs((prev) => ({ ...prev, [section.id]: e.target.value }))}
                placeholder="Ask for tone, bullets, shorter text..."
              />
              <button onClick={() => handleRefine(section)} disabled={busySection === section.id}>
                Apply prompt
              </button>
            </div>
            <div className="refine-block">
              <label>Comment</label>
              <textarea
                value={commentInputs[section.id] || ""}
                onChange={(e) => setCommentInputs((prev) => ({ ...prev, [section.id]: e.target.value }))}
                placeholder="Internal notes or reminders"
              />
              <button onClick={() => handleComment(section)} disabled={busySection === section.id}>
                Save comment
              </button>
              {section.last_comment && <p className="note">Last note: {section.last_comment}</p>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

