import HeroSection from '../components/landing/HeroSection'
import HowItWorks from '../components/landing/HowItWorks'
import VoiceClone from '../components/landing/VoiceClone'
import Research from '../components/landing/Research'
import Testimonials from '../components/landing/Testimonials'
import Pricing from '../components/landing/Pricing'
import CTA from '../components/landing/CTA'

export default function LandingPage() {
  return (
    <div className="bg-navy-950">
      <HeroSection />
      <HowItWorks />
      <VoiceClone />
      <Research />
      <Testimonials />
      <Pricing />
      <CTA />
    </div>
  )
}
