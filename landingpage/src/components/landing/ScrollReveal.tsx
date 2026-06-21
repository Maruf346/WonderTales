import { useEffect, useRef, useState } from 'react'
import type { ReactNode } from 'react'

interface ScrollRevealProps {
  children: ReactNode
  delay?: number
  duration?: number
  direction?: 'up' | 'down' | 'left' | 'right' | 'none'
  scale?: boolean
}

export default function ScrollReveal({
  children,
  delay = 0,
  duration = 1000,
  direction = 'up',
  scale = false,
}: ScrollRevealProps) {
  const [isIntersecting, setIsIntersecting] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsIntersecting(true)
          if (ref.current) observer.unobserve(ref.current)
        }
      },
      {
        threshold: 0.05,
        rootMargin: '0px 0px -60px 0px',
      }
    )

    if (ref.current) {
      observer.observe(ref.current)
    }

    return () => {
      observer.disconnect()
    }
  }, [])

  const getTransform = () => {
    if (isIntersecting) return 'translate(0, 0) scale(1)'

    let translate = ''
    switch (direction) {
      case 'up':
        translate = 'translateY(40px)'
        break
      case 'down':
        translate = 'translateY(-40px)'
        break
      case 'left':
        translate = 'translateX(40px)'
        break
      case 'right':
        translate = 'translateX(-40px)'
        break
      default:
        translate = 'translate(0,0)'
    }

    return `${translate} ${scale ? 'scale(0.95)' : ''}`
  }

  return (
    <div
      ref={ref}
      style={{
        opacity: isIntersecting ? 1 : 0,
        transform: getTransform(),
        transitionProperty: 'opacity, transform',
        transitionDuration: `${duration}ms`,
        transitionDelay: `${delay}ms`,
        transitionTimingFunction: 'cubic-bezier(0.16, 1, 0.3, 1)',
        willChange: 'opacity, transform',
      }}
    >
      {children}
    </div>
  )
}
