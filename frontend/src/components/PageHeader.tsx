interface PageHeaderProps {
  title: string;
  description: string;
  eyebrow?: string;
}

export default function PageHeader({ title, description, eyebrow }: PageHeaderProps) {
  return (
    <header className="mb-8 animate-fade-up">
      {eyebrow && (
        <p className="mb-1 text-xs font-semibold uppercase tracking-[0.2em] text-brand">{eyebrow}</p>
      )}
      <h1 className="font-display text-3xl font-bold text-white">{title}</h1>
      <p className="mt-2 max-w-2xl text-sm text-slate-400">{description}</p>
    </header>
  );
}
