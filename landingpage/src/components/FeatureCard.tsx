import type { ReactNode } from 'react'

interface FeatureCardProps {
  title: string
  description: string
  icon: ReactNode
}

export default function FeatureCard({ title, description, icon }: FeatureCardProps) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-[0_20px_80px_rgba(6,8,20,0.35)] backdrop-blur-xl">
      <div className="mb-5 inline-flex h-14 w-14 items-center justify-center rounded-3xl bg-orange-400/10 text-orange-300 shadow-lg shadow-orange-500/10">
        {icon}
      </div>
      <h3 className="mb-3 text-lg font-semibold text-white">{title}</h3>
      <p className="text-sm leading-6 text-slate-300">{description}</p>
    </div>
  )
}
