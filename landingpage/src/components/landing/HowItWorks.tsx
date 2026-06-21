import howItWorksImage from '../../assets/howitworksimg.svg'
import hiwBgImg from '../../assets/hiwbgimg.svg'
import icon1 from '../../assets/cartoon-boy-with-backpack-tablet 1.png'
import icon2 from '../../assets/image 20.png'
import icon3 from '../../assets/image 22.png'
import ScrollReveal from './ScrollReveal'

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="relative overflow-hidden px-6 pt-24 pb-0 md:py-28 lg:px-8 min-h-[700px] flex flex-col md:flex-row items-center bg-navy-950">
      
      {/* Actual Starry Constellation Background Vector */}
      <img 
        src={hiwBgImg} 
        alt="" 
        className="absolute inset-0 w-full h-full object-cover z-0 pointer-events-none opacity-60"
      />

      {/* Content wrapper */}
      <div className="relative z-10 mx-auto w-full max-w-7xl">
        <div className="max-w-2xl space-y-12">
          <ScrollReveal direction="up">
            <div>
              <p className="text-sm font-medium text-gold tracking-widest uppercase">How It Works</p>
              <h2 className="mt-4 font-serif text-4xl text-white sm:text-5xl lg:text-6xl leading-[1.1]">
                Create Magical Stories<br />in <span className="text-gold">3</span> Simple Steps
              </h2>
            </div>
          </ScrollReveal>

          <div className="grid gap-6 sm:grid-cols-3 pb-12 md:pb-0">
            {[
              { icon: icon1, title: 'Create Your Child', desc: 'Create or select profile to personalize their story.' },
              { icon: icon2, title: 'Create Story', desc: 'Choose a theme, length & Voice to generate a story.' },
              { icon: icon3, title: 'Listen & Enjoy', desc: 'Sit back, relax & enjoy magical story anytime anywhere.' },
            ].map((s, index) => (
              <ScrollReveal key={s.title} delay={index * 150} scale>
                <div className="rounded-2xl border border-white/10 bg-transparent p-6 text-left hover:border-gold/30 transition-all duration-300 h-full">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-navy-800 border border-white/10 mb-4 p-2">
                    <img src={s.icon} alt="" className="w-full h-full object-contain" />
                  </div>
                  <h3 className="text-sm font-medium text-gold">{s.title}</h3>
                  <p className="mt-2 text-xs text-white/60 font-light leading-relaxed">{s.desc}</p>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </div>

      {/* 2. Father-Daughter Illustration */}
      <div className="relative md:absolute bottom-0 right-0 w-full md:w-[40%] lg:w-[35%] h-[350px] md:h-[90%] max-h-[600px] z-0 pointer-events-none mt-auto">
        <ScrollReveal direction="left" duration={1200}>
          <img 
            src={howItWorksImage} 
            alt="" 
            className="w-full h-full object-contain md:object-right-bottom object-bottom"
          />
        </ScrollReveal>
      </div>
    </section>
  )
}


