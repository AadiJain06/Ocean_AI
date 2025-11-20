export type DocType = "docx" | "pptx";

export type ProjectStatus = "draft" | "generating" | "ready";

export type FeedbackChoice = "like" | "dislike";

export type Section = {
  id: number;
  title: string;
  position: number;
  content: string;
  feedback?: FeedbackChoice | null;
  last_comment?: string | null;
  created_at: string;
  updated_at: string;
};

export type Project = {
  id: number;
  title: string;
  topic: string;
  doc_type: DocType;
  status: ProjectStatus;
  created_at: string;
  updated_at: string;
};

export type ProjectDetail = Project & {
  sections: Section[];
};

