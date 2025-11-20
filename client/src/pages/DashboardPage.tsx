import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";
import type { Project } from "../types";

export function DashboardPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await api.get<Project[]>("/projects/");
        setProjects(data);
      } catch (err: any) {
        setError(err.response?.data?.detail || "Failed to load projects");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Projects</h1>
          <p>Pick up where you left off or start fresh.</p>
        </div>
        <Link to="/projects/new" className="primary">
          New project
        </Link>
      </div>
      {loading && <p>Loading...</p>}
      {error && <div className="error">{error}</div>}
      {!loading && projects.length === 0 && <p>No projects yet.</p>}
      <div className="card-grid">
        {projects.map((project) => (
          <Link key={project.id} to={`/projects/${project.id}`} className="card">
            <h3>{project.title}</h3>
            <p>{project.topic}</p>
            <div className="tag-row">
              <span className="tag">{project.doc_type.toUpperCase()}</span>
              <span className={`status ${project.status}`}>{project.status}</span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

