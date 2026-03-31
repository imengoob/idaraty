export default function FeatureCard({ icon, title, subtitle }) {
  return (
    <div className="bg-white/20 rounded-2xl shadow-soft p-6 text-center w-full max-w-xs fade-in">
      <div className="mx-auto mb-3 w-12 h-12 rounded-full bg-black/10 flex items-center justify-center">
        {icon}
      </div>
      <div className="feature-card-title text-lg">{title}</div>
      <div className="feature-card-subtitle mt-1 text-sm">{subtitle}</div>
    </div>
  );
}
