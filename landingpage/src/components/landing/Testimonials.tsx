import avatar1 from '../../assets/avatar1.svg'
import avatar2 from '../../assets/avatar2.svg'
import avatar3 from '../../assets/avatar3.svg'
import avatar4 from '../../assets/avatar4.svg'
import ScrollReveal from './ScrollReveal'

export default function Testimonials() {
  return (
    <section className="px-6 py-16 lg:px-8">
      <div className="mx-auto max-w-7xl text-center">
        <ScrollReveal direction="up">
          <h2 className="font-serif text-4xl text-gold sm:text-5xl">Testimonials</h2>
          <p className="mt-4 text-sm font-light text-white/70">Trusted by parents & loved by thousands of families</p>
        </ScrollReveal>

        <div className="mt-16 grid sm:grid-cols-2 relative">
          {/* Grid borders */}
          <div className="absolute top-1/2 left-0 right-0 h-px bg-white/10 hidden sm:block"></div>
          <div className="absolute top-0 bottom-0 left-1/2 w-px bg-white/10 hidden sm:block"></div>

          {[
            { name: 'Neil Sims', avatar: avatar1, headline: 'StoryTime AI has transformed our family nights', quote: '"StoryTime AI has been a game-changer for our family. The personalized stories captivate my child\'s imagination, and the voice cloning feature adds a comforting touch. Bedtime has never been so magical!"' },
            { name: 'Micheal Gough', avatar: avatar2, headline: 'StoryTime AI: Crafting magical moments, one bedtime story at a time', quote: '"StoryTime AI is pure magic! As a busy parent, I love how easily I can create personalized stories with my voice. My kids adore hearing stories narrated by me, even when I\'m away. It\'s heartwarming and so convenient!"' },
            { name: 'Helene Engels', avatar: avatar3, headline: 'Revolutionized our storytelling experience', quote: '"As a mom, StoryTime AI is a dream. I can create personalized stories with my voice, even when I\'m traveling. My kids love hearing stories narrated by me, and it brings us closer. It\'s a heartwarming and convenient way to connect!"' },
            { name: 'Karen Nelson', avatar: avatar4, headline: 'Parents rave about the voice cloning feature', quote: '"StoryTime AI has become a cherished part of our nightly routine. The personalized stories are enchanting, and my kids are thrilled to hear tales in my own voice, even when I\'m traveling. It\'s a magical way to stay connected!"' },
          ].map((t, i) => (
            <ScrollReveal key={t.name} delay={i * 150} scale>
              <div className={`p-10 text-center ${i < 2 ? 'sm:pb-16' : 'sm:pt-16'} h-full`}>
                <div className="flex items-center justify-center gap-3 mb-6">
                  <img src={t.avatar} alt={t.name} className="h-8 w-8 rounded-full object-cover" />
                  <p className="text-sm font-medium text-white">{t.name}</p>
                </div>
                <h3 className="text-base font-semibold text-white leading-snug">{t.headline}</h3>
                <p className="mt-4 text-[13px] text-white/60 font-light leading-relaxed max-w-md mx-auto">{t.quote}</p>
              </div>
            </ScrollReveal>
          ))}
        </div>

        <ScrollReveal delay={200} scale>
          <button className="mt-12 rounded-lg bg-gradient-to-b from-orange-300 to-orange-500 px-8 py-2.5 text-[13px] font-semibold text-white shadow-lg hover:opacity-90">
            Show more...
          </button>
        </ScrollReveal>
      </div>
    </section>
  )
}
