import footerImg from '../../assets/footerimg.png'
import storeButtons from '../../assets/google and apple playstore.svg'

export default function CTA() {
  return (
    <section className="relative w-full overflow-hidden min-h-[460px] flex items-center bg-navy-950 border-t border-white/10">
      
      {/* Background Image positioned to show the house on the right, full-bleed */}
      <img 
        src={footerImg} 
        alt="" 
        className="absolute inset-0 w-full h-full object-cover object-right z-0 pointer-events-none"
      />
      
      {/* Beautiful Gradient overlay to darken the left side and fade to show the house on the right */}
      <div className="absolute inset-0 bg-gradient-to-r from-navy-950 via-navy-950/60 to-transparent z-0" />

      {/* Content Wrapper aligned to the standard page layout grid */}
      <div className="relative z-10 mx-auto w-full max-w-7xl px-6 py-20 lg:px-8">
        <div className="max-w-xl text-left space-y-4">
          <p className="text-xs font-semibold text-gold tracking-widest uppercase">Ready to Begin?</p>
          <h2 className="font-serif text-3xl sm:text-4xl lg:text-5xl text-white leading-[1.15]">
            Start Your Child's<br />Magical Journey Tonight
          </h2>
          <p className="text-sm sm:text-base text-white/70 font-light max-w-md leading-relaxed">
            Download the app and create unforgettable bedtime memories.
          </p>
          <div className="pt-4 flex justify-start">
            <img 
              src={storeButtons} 
              alt="Download on App Store and Google Play" 
              className="h-10 md:h-12 object-contain hover:opacity-90 transition cursor-pointer" 
            />
          </div>
        </div>
      </div>
    </section>
  )
}
