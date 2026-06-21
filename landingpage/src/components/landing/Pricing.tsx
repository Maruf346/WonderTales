import checkCircle from '../../assets/check-circle.svg'
import ScrollReveal from './ScrollReveal'

export default function Pricing() {
  return (
    <section id="pricing" className="px-6 py-24 lg:px-8">
      <div className="mx-auto max-w-7xl text-center">
        <ScrollReveal direction="up">
          <p className="text-sm font-medium text-gold tracking-widest uppercase">Choose Your Plan</p>
          <h2 className="mt-4 font-serif text-4xl text-white sm:text-5xl leading-tight">
            Choose The Right<br />Plan for You
          </h2>
        </ScrollReveal>

        <div className="mt-16 grid gap-6 sm:grid-cols-3 max-w-5xl mx-auto">
          {[
            { name: 'Discovery', price: '€1.99', desc: 'Perfect for new users – begin your style transformation', features: ['3 AI stories', 'Save & replay'], bg: 'bg-white/10', glow: 'shadow-2xl' },
            { name: 'Classic', price: '€4.99', desc: 'Enjoy Full Access With a Flexible Monthly Plan', features: ['9 AI stories', 'Save & replay'], bg: 'bg-[#67A4FF]', glow: 'shadow-[0_0_50px_rgba(103,164,255,0.45)]' },
            { name: 'Premium', price: '€14.99', desc: 'Maximize Savings With Annual Access', features: ['9 AI generated stories', '3 family voice stories'], bg: 'bg-[#1E67D6]', glow: 'shadow-[0_0_50px_rgba(30,103,214,0.55)]' },
          ].map((p, index) => (
            <ScrollReveal key={p.name} delay={index * 150} scale>
              <div className={`rounded-2xl p-8 text-left ${p.bg} ${p.glow} border border-white/10 hover:scale-[1.02] transition-all duration-300 h-full`}>
                <p className="text-base font-medium text-white">{p.name}</p>
                <p className="mt-4 font-bold text-white text-4xl flex items-baseline gap-1">
                  {p.price} <span className="text-[11px] font-medium text-white/80">/month</span>
                </p>
                <p className="mt-4 text-xs text-white/80 font-light leading-relaxed min-h-[40px]">{p.desc}</p>
                <ul className="mt-8 space-y-4">
                  {p.features.map((f) => (
                    <li key={f} className="flex items-center gap-3 text-xs text-white/90 font-light">
                      <img src={checkCircle} alt="check" className="w-4 h-4" />
                      {f}
                    </li>
                  ))}
                </ul>
              </div>
            </ScrollReveal>
          ))}
        </div>
      </div>
    </section>
  )
}
