import { useEffect, useState } from 'react'

interface Sparkle {
  id: number
  x: number
  y: number
  size: number
  color: string
  velocity: { x: number; y: number }
  alpha: number
}

export default function MagicCursor() {
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const [sparkles, setSparkles] = useState<Sparkle[]>([])
  const [isVisible, setIsVisible] = useState(false)
  const [isTouchDevice, setIsTouchDevice] = useState(true)

  useEffect(() => {
    // Detect touch device
    const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0
    setIsTouchDevice(isTouch)
    if (isTouch) return

    // Hide default cursor on desktop
    document.body.classList.add('custom-cursor-active')

    const onMouseMove = (e: MouseEvent) => {
      setPosition({ x: e.clientX, y: e.clientY })
      setIsVisible(true)

      // Add a sparkling magic particle
      const colors = ['#E8A020', '#F5C060', '#FFE090', '#3B82F6', '#60A5FA']
      const randomColor = colors[Math.floor(Math.random() * colors.length)]
      
      const newSparkle: Sparkle = {
        id: Math.random(),
        x: e.clientX,
        y: e.clientY,
        size: Math.random() * 8 + 4,
        color: randomColor,
        velocity: {
          x: (Math.random() - 0.5) * 3,
          y: (Math.random() - 0.5) * 3 + 0.8, // slight gravity fall
        },
        alpha: 1,
      }

      setSparkles((prev) => [...prev.slice(-25), newSparkle]) // keep performance high
    }

    const onMouseLeave = () => {
      setIsVisible(false)
    }

    window.addEventListener('mousemove', onMouseMove)
    document.addEventListener('mouseleave', onMouseLeave)
    
    return () => {
      window.removeEventListener('mousemove', onMouseMove)
      document.removeEventListener('mouseleave', onMouseLeave)
      document.body.classList.remove('custom-cursor-active')
    }
  }, [])

  // Animate the sparkling trails
  useEffect(() => {
    if (isTouchDevice) return

    const interval = setInterval(() => {
      setSparkles((prev) =>
        prev
          .map((s) => ({
            ...s,
            x: s.x + s.velocity.x,
            y: s.y + s.velocity.y,
            alpha: s.alpha - 0.04, // smooth fade out
          }))
          .filter((s) => s.alpha > 0)
      )
    }, 24)

    return () => clearInterval(interval)
  }, [isTouchDevice])

  if (isTouchDevice || !isVisible) return null

  return (
    <>
      {/* 1. Main Glowing Magic Wand Star Cursor */}
      <div
        className="fixed pointer-events-none z-50 -translate-x-1/2 -translate-y-1/2 mix-blend-screen transition-transform duration-75 ease-out"
        style={{
          left: position.x,
          top: position.y,
        }}
      >
        {/* Soft Golden Glow Ring */}
        <div className="absolute inset-0 w-8 h-8 -left-4 -top-4 rounded-full bg-gold/30 blur-md animate-pulse" />
        
        {/* Star Sparkle Icon */}
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="text-gold drop-shadow-[0_0_8px_rgba(232,160,32,0.9)]"
        >
          <path
            d="M12 2L14.8 9.2L22 12L14.8 14.8L12 22L9.2 14.8L2 12L9.2 9.2L12 2Z"
            fill="currentColor"
          />
        </svg>
      </div>

      {/* 2. Sparkles Trail */}
      {sparkles.map((s) => (
        <div
          key={s.id}
          className="fixed pointer-events-none z-50 -translate-x-1/2 -translate-y-1/2 select-none"
          style={{
            left: s.x,
            top: s.y,
            opacity: s.alpha,
            transform: `translate(-50%, -50%) scale(${s.alpha})`,
          }}
        >
          <svg
            width={s.size}
            height={s.size}
            viewBox="0 0 24 24"
            fill="none"
            style={{ color: s.color }}
          >
            <path
              d="M12 2L14.8 9.2L22 12L14.8 14.8L12 22L9.2 14.8L2 12L9.2 9.2L12 2Z"
              fill="currentColor"
            />
          </svg>
        </div>
      ))}
    </>
  )
}
