interface GlassButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger'
}

export function GlassButton({ variant = 'primary', className = '', children, ...props }: GlassButtonProps) {
  const variants = {
    primary: 'bg-primary-500 hover:bg-primary-400 hover:-translate-y-0.5 transition-all text-white',
    secondary: 'bg-white/5 hover:bg-white/10 text-text-high border border-white/10',
    danger: 'bg-red-600/80 hover:bg-red-500/80 text-white',
  }

  return (
    <button
      className={`px-4 py-2.5 rounded-xl font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}
