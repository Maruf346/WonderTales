import logoIcon from '../assets/logo.svg'
import fbIcon from '../assets/Facebook.svg'
import igIcon from '../assets/Instagram.svg'
import twIcon from '../assets/Twitter.svg'

export default function Footer() {
  return (
    <footer className="bg-navy-950 px-6 pt-24 pb-8 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-10">
          <div className="flex items-center justify-center md:justify-start">
            <img src={logoIcon} alt="WonderTales Hub" className="h-32 object-contain" />
          </div>
          <div className="space-y-4 text-[13px] text-white/80 font-light text-center md:text-right pb-4">
            <p>Contact E-mail: <a href="mailto:hello@wondertales.com" className="hover:text-gold transition">hello@wondertales.com</a></p>
            <p>Support E-mail: <a href="mailto:support@wondertales.com" className="hover:text-gold transition">support@wondertales.com</a></p>
          </div>
        </div>

        <hr className="my-8 border-white/10" />

        <div className="flex flex-col items-center justify-between gap-6 sm:flex-row">
          <p className="text-[13px] text-white/50 font-light">© 2026 Wonder Tales Hub, Inc. All rights reserved.</p>
          <div className="flex items-center gap-4">
            <a href="#" className="transition hover:opacity-80">
              <img src={twIcon} alt="Twitter" className="h-8 w-8" />
            </a>
            <a href="#" className="transition hover:opacity-80">
              <img src={igIcon} alt="Instagram" className="h-8 w-8" />
            </a>
            <a href="#" className="transition hover:opacity-80">
              <img src={fbIcon} alt="Facebook" className="h-8 w-8" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
