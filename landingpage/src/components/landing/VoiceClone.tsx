import waveImg from '../../assets/wave.svg'
import micImg from '../../assets/mic.svg'
import handImg from '../../assets/handimg.svg'

export default function VoiceClone() {
  return (
    <section id="voice" className="relative px-6 py-12 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <div className="relative rounded-[2rem] border border-white/10 bg-navy-900/50 p-6 sm:p-10 lg:p-16 shadow-2xl shadow-black/40 mt-10">
          
          <div className="absolute inset-0 overflow-hidden rounded-[2rem] opacity-25 z-0 pointer-events-none">
             <img src={waveImg} alt="" className="w-full h-full object-cover" />
          </div>
 
          <div className="relative z-10 flex flex-col gap-12 lg:flex-row lg:items-center justify-between w-full min-h-[300px]">
            <div className="max-w-md space-y-4 text-left z-20">
              <p className="text-xs font-semibold text-gold tracking-widest uppercase">Your Voice, Their Comfort</p>
              <h2 className="font-serif text-3xl sm:text-4xl lg:text-5xl text-white leading-tight">Clone Your Voice<br />in Seconds</h2>
              <p className="text-sm text-white/70 font-light leading-relaxed">
                Record your voice and let our AI create a perfect clone to narrate stories for your child.
              </p>
            </div>
            
            <div className="lg:absolute lg:left-1/2 lg:top-1/2 lg:-translate-x-1/2 lg:-translate-y-1/2 z-10 flex justify-center mt-4 lg:mt-0">
              {/* Glowing Glass Mic Circle */}
              <div className="flex h-20 w-20 items-center justify-center rounded-full border border-white/20 bg-white/5 backdrop-blur-md shadow-[0_0_40px_rgba(255,215,0,0.2)] hover:scale-110 transition-transform duration-300">
                <img src={micImg} alt="Mic" className="h-8 w-8 filter brightness-125" />
              </div>
            </div>
            
            <div className="relative z-20 hidden sm:flex justify-end lg:static mt-4 -mb-6 -mr-6 sm:-mb-10 sm:-mr-10 lg:m-0">
              {/* Hand with Phone Mockup */}
              <div className="h-[350px] sm:h-[450px] lg:h-[550px] lg:absolute lg:-right-16 lg:-bottom-[64px] shrink-0 hover:scale-105 transition-transform duration-500 pointer-events-none">
                <img src={handImg} alt="Mobile App in Hand" className="h-full w-auto object-right-bottom object-contain max-w-none drop-shadow-2xl pointer-events-auto" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
