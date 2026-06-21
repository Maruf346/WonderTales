import heroImage from '../../assets/herosectionimg.png'
import storeButtons from '../../assets/google and apple playstore.svg'
import bookIcon from '../../assets/Book.svg'
import booksIcon from '../../assets/Books.svg'
import aiMicIcon from '../../assets/AI Mic.svg'
import avatarUser1 from '../../assets/avatar1.svg'
import avatarUser2 from '../../assets/avatar2.svg'
import avatarUser3 from '../../assets/avatar3.svg'
import avatarUser4 from '../../assets/avatar4.svg'

export default function HeroSection() {
  return (
    <section className="relative min-h-[90vh] flex flex-col justify-end pb-16">
      {/* Background Image using absolute img tag for bulletproof rendering */}
      <img 
        src={heroImage} 
        alt="" 
        className="absolute inset-0 w-full h-full object-cover object-top z-0 pointer-events-none"
      />
      
      <div className="absolute inset-0 bg-navy-950/40 z-0" />
      <div className="absolute inset-x-0 bottom-0 h-64 bg-gradient-to-t from-navy-950 to-transparent z-0" />

      <div className="relative z-10 mx-auto w-full max-w-7xl px-6 lg:px-8 mt-32">
        <div className="max-w-2xl space-y-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-black/40 px-4 py-1.5 backdrop-blur-sm">
            <span className="text-gold text-lg leading-none">✨</span>
            <span className="text-xs text-white/80 font-light tracking-wider">AI Powered - Personal - Magic</span>
          </div>

          <h1 className="font-serif text-5xl leading-[1.1] tracking-wide text-white sm:text-6xl lg:text-[4.5rem]">
            EVRY NIGHT, A NEW<br />CHAPTER.<br />
            <span className="text-gold">THE SAME HERO.</span>
          </h1>

          <p className="max-w-md text-base text-white/90 font-light leading-relaxed">
            Create personalized bedtimestories for your child with the power of AI and your love.
          </p>

          {/* Store Buttons */}
          <div className="pt-2">
            <img src={storeButtons} alt="Download on App Store and Google Play" className="h-12 object-contain" />
          </div>

          {/* Avatars */}
          <div className="flex items-center gap-4 pt-4">
            <div className="flex -space-x-3">
              {[avatarUser1, avatarUser2, avatarUser3, avatarUser4].map((src, i) => (
                <img key={i} src={src} alt="" className="h-10 w-10 rounded-full border-2 border-navy-950 bg-navy-800 object-cover p-1" />
              ))}
            </div>
            <p className="text-sm text-white/80 font-light">Loved by <span className="text-gold font-medium">10,000+</span> parents around the world</p>
          </div>
        </div>
      </div>

      {/* ===== FEATURES STRIP ===== */}
      <div className="relative z-20 mx-auto w-full max-w-7xl px-6 lg:px-8 mt-16">
        <div className="rounded-3xl border border-white/20 bg-white/5 backdrop-blur-xl p-8 shadow-2xl">
          <div className="grid gap-8 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-white/10">
            {[
              { icon: bookIcon, title: 'AI Generated Stories', desc: 'Unique stories crafted for your childe' },
              { icon: aiMicIcon, title: 'Your Voice, Their Story', desc: 'Clone your voice & narrate their adventure' },
              { icon: booksIcon, title: 'Endless Adventure', desc: 'Unique stories for endless imagination' },
            ].map((f, idx) => (
              <div key={f.title} className={`flex items-center gap-5 ${idx !== 0 ? 'md:pl-8 pt-8 md:pt-0' : ''}`}>
                <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-white/10 to-transparent border border-white/10">
                  <img src={f.icon} alt="" className="h-7 w-7" />
                </div>
                <div>
                  <h3 className="text-base font-semibold text-gold">{f.title}</h3>
                  <p className="mt-1 text-sm text-white/60 font-light">{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
