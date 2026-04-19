interface GlassInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
}

export function GlassInput({ label, className = '', ...props }: GlassInputProps) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && <label className="text-sm text-text-muted font-medium">{label}</label>}
      <input
        className={`w-full px-4 py-3 rounded-xl bg-[rgba(200,210,255,0.04)] border border-[rgba(140,170,255,0.12)] text-text-high placeholder:text-text-subtle focus:outline-none focus:border-primary-500/50 focus:ring-1 focus:ring-primary-500/30 transition-colors ${className}`}
        {...props}
      />
    </div>
  )
}
