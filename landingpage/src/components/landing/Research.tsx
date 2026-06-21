import ScrollReveal from './ScrollReveal'

export default function Research() {
  return (
    <section className="px-6 py-24 lg:px-8">
      <div className="mx-auto max-w-7xl text-center">
        <ScrollReveal direction="up">
          <p className="text-sm font-medium text-gold tracking-widest uppercase">Backed By Science</p>
          <h2 className="mt-4 font-serif text-4xl text-white sm:text-5xl">The Research is Clear</h2>
          <p className="mx-auto mt-6 max-w-xl text-base text-white/70 font-light leading-relaxed">
            Wonder Tales Hub doesn't just entertain it builds habits and skills that science has proven matter.
          </p>
        </ScrollReveal>

        <div className="mt-16 grid gap-6 sm:grid-cols-3">
          {[
            { stat: '+1HR', desc: 'More sleep every night with a consistent bedtime routine.', ref: 'Mindell et al. — Journal Sleep, 2015.', link: 'Read Study ↗' },
            { stat: '1.5M', desc: 'More words heard by age 5 when read to every night.', ref: 'Logan JA et al. — Ohio State University, 2019.', link: '' },
            { stat: '3 IN 1', desc: 'Benefits: better sleep, literacy development, and emotional regulation.', ref: 'Mindell & Williamson — Sleep Medicine Reviews, 2018.', link: 'Read Study ↗' },
          ].map((c, index) => (
            <ScrollReveal key={c.stat} delay={index * 150} scale>
              <div className="flex flex-col h-full rounded-2xl border border-white/10 border-t-2 border-t-gold bg-navy-800/40 p-8 text-center transition hover:border-gold/30">
                <p className="text-3xl font-bold text-white tracking-wide">{c.stat}</p>
                <p className="mt-4 text-sm text-white/80 font-medium leading-relaxed px-4">{c.desc}</p>
                <p className="mt-8 text-[11px] text-white/50 font-light leading-relaxed flex-grow">
                  {c.stat === '+1HR' && 'A multinational study of 10,085 families across 14 countries found children with a nightly routine sleep over an hour more per night — and the benefit grows the more consistent the routine'}
                  {c.stat === '1.5M' && 'Ohio State University found children read to five times a week hear 1.5 million more words by age five than children not read to — building the vocabulary foundation for lifelong reading success.'}
                  {c.stat === '3 IN 1' && 'A review in Sleep Medicine Reviews found bedtime routines benefit not just sleep, but also child literacy outcomes, mood, emotional-behavioural regulation, and parent-child bonding.'}
                </p>
                <div className="mt-6 pt-4 border-t border-white/5 w-full">
                   <p className="text-[11px] text-white/60 mb-1">{c.ref}</p>
                   {c.link && <a href="#" className="text-xs font-medium text-gold hover:underline">{c.link}</a>}
                </div>
              </div>
            </ScrollReveal>
          ))}
        </div>
      </div>
    </section>
  )
}
