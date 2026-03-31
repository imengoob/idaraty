export default function ModelSelector({ value, onChange, usingLabel }) {
  return (
    <div className="flex items-center gap-3 flex-wrap justify-center">
      <label className="inline-flex items-center gap-2 cursor-pointer">
        <input type="radio" name="model" value="gemini"
               checked={value === "gemini"} onChange={e => onChange(e.target.value)} />
        <span>Gemini</span>
      </label>
      <label className="inline-flex items-center gap-2 cursor-pointer">
        <input type="radio" name="model" value="qwen"
               checked={value === "qwen"} onChange={e => onChange(e.target.value)} />
        <span>Qwen</span>
      </label>
      <span className="px-2 py-1 rounded-full bg-white/10 text-xs">
        {usingLabel || `Using ${value}`}
      </span>
    </div>
  );
}
