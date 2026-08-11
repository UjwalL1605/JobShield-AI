import { useEffect, useRef } from 'react'
import './CyberCanvas3D.css'

export default function CyberCanvas3D() {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let animationFrameId
    let width = (canvas.width = window.innerWidth)
    let height = (canvas.height = window.innerHeight)

    let mouseX = width / 2
    let mouseY = height / 2
    let targetMouseX = width / 2
    let targetMouseY = height / 2

    const handleMouseMove = (e) => {
      targetMouseX = e.clientX
      targetMouseY = e.clientY
    }

    const handleResize = () => {
      width = canvas.width = window.innerWidth
      height = canvas.height = window.innerHeight
      initThreatNodes()
    }

    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('resize', handleResize)

    // ── 3D Security Shield Model Geometry (Apex, Shoulders, Body, Tip) ──────
    // 3D vertices defining the JobShield 3D Defense Crest
    const shieldVertices = [
      // Outer Shield Boundary
      { x: 0, y: -160, z: 0 },     // 0: Top Crest Peak
      { x: 70, y: -145, z: 25 },   // 1: Top Right Corner
      { x: -70, y: -145, z: 25 },  // 2: Top Left Corner
      { x: 130, y: -70, z: 50 },   // 3: Right Shoulder
      { x: -130, y: -70, z: 50 },  // 4: Left Shoulder
      { x: 110, y: 50, z: 35 },    // 5: Mid-Right Flank
      { x: -110, y: 50, z: 35 },   // 6: Mid-Left Flank
      { x: 65, y: 130, z: 20 },    // 7: Lower Right Taper
      { x: -65, y: 130, z: 20 },   // 8: Lower Left Taper
      { x: 0, y: 190, z: 0 },      // 9: Bottom Shield Point

      // Inner Core / Central Spine
      { x: 0, y: -90, z: 65 },     // 10: Inner Top Center
      { x: 55, y: -20, z: 75 },    // 11: Inner Right Core
      { x: -55, y: -20, z: 75 },   // 12: Inner Left Core
      { x: 0, y: 60, z: 60 },      // 13: Inner Lower Center
      { x: 0, y: 125, z: 35 },     // 14: Inner Bottom Spine

      // Back Armor Plate (for 3D depth)
      { x: 0, y: -140, z: -40 },   // 15: Back Top
      { x: 90, y: -50, z: -50 },   // 16: Back Right Shoulder
      { x: -90, y: -50, z: -50 },  // 17: Back Left Shoulder
      { x: 0, y: 160, z: -40 },    // 18: Back Bottom Point
    ]

    // Shield Wireframe Edges
    const shieldEdges = [
      // Outer Contour
      [0, 1], [1, 3], [3, 5], [5, 7], [7, 9],
      [0, 2], [2, 4], [4, 6], [6, 8], [8, 9],
      [1, 2], // Top Crest Bar

      // Inner Reinforcements & Core Synapses
      [0, 10], [10, 11], [10, 12], [11, 13], [12, 13], [13, 14], [14, 9],
      [1, 11], [2, 12], [3, 11], [4, 12], [5, 13], [6, 13], [7, 14], [8, 14],

      // Depth Struts to Back Plate
      [0, 15], [3, 16], [4, 17], [9, 18],
      [15, 16], [15, 17], [16, 18], [17, 18],
    ]

    // ── Floating Threat Nodes & Orbital Defense Constellation ───────────────
    let threatNodes = []
    function initThreatNodes() {
      threatNodes = []
      const count = Math.min(60, Math.floor((width * height) / 22000))
      for (let i = 0; i < count; i++) {
        const angle = Math.random() * Math.PI * 2
        const radius = Math.random() * 550 + 120
        threatNodes.push({
          x: Math.cos(angle) * radius,
          y: Math.sin(angle) * (radius * 0.7) + (Math.random() - 0.5) * 200,
          z: Math.random() * 600 - 300,
          vx: (Math.random() - 0.5) * 0.5,
          vy: (Math.random() - 0.5) * 0.5,
          vz: (Math.random() - 0.5) * 0.4,
          size: Math.random() * 2.5 + 1.5,
          type: Math.random() > 0.7 ? 'scam' : 'shield', // Red threat or green security node
        })
      }
    }

    initThreatNodes()

    let rotY = 0
    let rotX = 0.15
    let radarPulseAngle = 0
    const fov = 600

    // ── Render Loop ─────────────────────────────────────────────────────────
    const render = () => {
      // Smooth mouse follow
      mouseX += (targetMouseX - mouseX) * 0.04
      mouseY += (targetMouseY - mouseY) * 0.04

      ctx.clearRect(0, 0, width, height)

      const isLight = document.documentElement.getAttribute('data-theme') === 'light'

      // Center position of 3D Shield Model
      const centerX = width > 1024 ? width * 0.75 : width / 2
      const centerY = width > 1024 ? height * 0.42 : height * 0.35

      // Shield 3D Rotation Animation
      rotY += 0.007
      rotX = 0.15 + (mouseY - height / 2) * 0.0003
      radarPulseAngle += 0.025

      // ── 1. Draw 3D Orbiting Radar Rings Around Shield ──
      const ringRadiusX = 260
      const ringRadiusY = 90
      ctx.save()
      ctx.translate(centerX + (mouseX - width / 2) * 0.03, centerY + (mouseY - height / 2) * 0.03)

      // Outer Radar Orbit
      ctx.beginPath()
      ctx.ellipse(0, 20, ringRadiusX, ringRadiusY, rotX, 0, Math.PI * 2)
      ctx.strokeStyle = isLight ? 'rgba(5, 150, 105, 0.35)' : 'rgba(0, 229, 153, 0.25)'
      ctx.lineWidth = isLight ? 1.5 : 1.0
      ctx.setLineDash([6, 8])
      ctx.stroke()
      ctx.setLineDash([])

      // Inner Radar Orbit
      ctx.beginPath()
      ctx.ellipse(0, 20, ringRadiusX * 0.65, ringRadiusY * 0.65, rotX, 0, Math.PI * 2)
      ctx.strokeStyle = isLight ? 'rgba(8, 145, 178, 0.3)' : 'rgba(0, 240, 255, 0.2)'
      ctx.lineWidth = 1.0
      ctx.stroke()

      // Radar Sweeper Beam
      const sweepX = Math.cos(radarPulseAngle) * ringRadiusX
      const sweepY = Math.sin(radarPulseAngle) * ringRadiusY + 20
      ctx.beginPath()
      ctx.moveTo(0, 20)
      ctx.lineTo(sweepX, sweepY)
      ctx.strokeStyle = isLight ? 'rgba(5, 150, 105, 0.6)' : 'rgba(0, 229, 153, 0.6)'
      ctx.lineWidth = 2
      ctx.stroke()

      // Sweeper Point Dot
      ctx.beginPath()
      ctx.arc(sweepX, sweepY, 4, 0, Math.PI * 2)
      ctx.fillStyle = isLight ? '#059669' : '#00e599'
      ctx.shadowColor = '#00e599'
      ctx.shadowBlur = 8
      ctx.fill()
      ctx.shadowBlur = 0
      ctx.restore()

      // ── 2. Draw 3D Threat Constellation Particles ──
      const projectedThreats = []
      threatNodes.forEach((node) => {
        node.x += node.vx
        node.y += node.vy
        node.z += node.vz

        if (node.x < -width / 2) node.x = width / 2
        if (node.x > width / 2) node.x = -width / 2
        if (node.y < -height / 2) node.y = height / 2
        if (node.y > height / 2) node.y = -height / 2
        if (node.z < -300) node.z = 300
        if (node.z > 300) node.z = -300

        const zDist = node.z + 500
        const scale = fov / zDist
        const px = node.x * scale + centerX + (mouseX - width / 2) * 0.02
        const py = node.y * scale + centerY + (mouseY - height / 2) * 0.02

        projectedThreats.push({ px, py, scale, type: node.type, size: node.size, z: node.z })

        const alpha = Math.max(0.2, (node.z + 300) / 600 * (isLight ? 0.6 : 0.8))
        ctx.beginPath()
        ctx.arc(px, py, node.size * scale, 0, Math.PI * 2)
        ctx.fillStyle = node.type === 'scam'
          ? isLight ? `rgba(220, 38, 38, ${alpha})` : `rgba(239, 68, 68, ${alpha})`
          : isLight ? `rgba(5, 150, 105, ${alpha})` : `rgba(0, 229, 153, ${alpha})`
        ctx.fill()
      })

      // Threat Rays connecting nearby nodes
      for (let i = 0; i < projectedThreats.length; i++) {
        for (let j = i + 1; j < projectedThreats.length; j++) {
          const n1 = projectedThreats[i]
          const n2 = projectedThreats[j]
          const dx = n1.px - n2.px
          const dy = n1.py - n2.py
          const dist = Math.sqrt(dx * dx + dy * dy)

          if (dist < 90) {
            const alpha = (1 - dist / 90) * (isLight ? 0.3 : 0.2)
            ctx.beginPath()
            ctx.moveTo(n1.px, n1.py)
            ctx.lineTo(n2.px, n2.py)
            ctx.strokeStyle = isLight
              ? `rgba(15, 23, 42, ${alpha})`
              : `rgba(0, 240, 255, ${alpha})`
            ctx.lineWidth = isLight ? 0.8 : 0.6
            ctx.stroke()
          }
        }
      }

      // ── 3. Transform & Render 3D Cyber Shield Model ──
      const projectedShield = shieldVertices.map((v) => {
        // Rotate around Y-axis
        const x1 = v.x * Math.cos(rotY) - v.z * Math.sin(rotY)
        const z1 = v.x * Math.sin(rotY) + v.z * Math.cos(rotY)

        // Rotate around X-axis
        const y2 = v.y * Math.cos(rotX) - z1 * Math.sin(rotX)
        const z2 = v.y * Math.sin(rotX) + z1 * Math.cos(rotX)

        const zDist = z2 + 450
        const scale = fov / zDist
        const projX = x1 * scale + centerX + (mouseX - width / 2) * 0.04
        const projY = y2 * scale + centerY + (mouseY - height / 2) * 0.04

        return { x: projX, y: projY, z: z2, scale }
      })

      // Render 3D Shield Wireframe Lines
      ctx.lineWidth = isLight ? 1.8 : 1.4
      shieldEdges.forEach(([i, j]) => {
        const p1 = projectedShield[i]
        const p2 = projectedShield[j]
        const avgZ = (p1.z + p2.z) / 2

        // Depth opacity
        const depthAlpha = Math.max(0.15, Math.min(1.0, (avgZ + 100) / 200 * (isLight ? 0.8 : 0.95)))

        const grad = ctx.createLinearGradient(p1.x, p1.y, p2.x, p2.y)
        if (isLight) {
          grad.addColorStop(0, `rgba(5, 150, 105, ${depthAlpha})`)
          grad.addColorStop(0.5, `rgba(8, 145, 178, ${depthAlpha})`)
          grad.addColorStop(1, `rgba(79, 70, 229, ${depthAlpha * 0.85})`)
        } else {
          grad.addColorStop(0, `rgba(0, 229, 153, ${depthAlpha})`)
          grad.addColorStop(0.5, `rgba(0, 240, 255, ${depthAlpha * 1.1})`)
          grad.addColorStop(1, `rgba(168, 85, 247, ${depthAlpha * 0.9})`)
        }

        ctx.beginPath()
        ctx.moveTo(p1.x, p1.y)
        ctx.lineTo(p2.x, p2.y)
        ctx.strokeStyle = grad
        ctx.stroke()
      })

      // Render 3D Shield Nodes / Security Anchors
      projectedShield.forEach((p, idx) => {
        const vAlpha = Math.max(0.3, (p.z + 100) / 200)
        ctx.beginPath()
        const nodeRadius = (idx === 0 || idx === 9 || idx === 10 || idx === 13) ? 5 : 3.5
        ctx.arc(p.x, p.y, nodeRadius * p.scale, 0, Math.PI * 2)

        if (isLight) {
          ctx.fillStyle = idx === 0 || idx === 9 
            ? `rgba(8, 145, 178, ${vAlpha})` 
            : `rgba(5, 150, 105, ${vAlpha})`
          ctx.shadowColor = '#059669'
          ctx.shadowBlur = 6
        } else {
          ctx.fillStyle = idx === 0 || idx === 9 
            ? `rgba(0, 240, 255, ${vAlpha})` 
            : `rgba(0, 229, 153, ${vAlpha})`
          ctx.shadowColor = '#00e599'
          ctx.shadowBlur = 10
        }

        ctx.fill()
        ctx.shadowBlur = 0
      })

      animationFrameId = requestAnimationFrame(render)
    }

    render()

    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('resize', handleResize)
      cancelAnimationFrame(animationFrameId)
    }
  }, [])

  return <canvas ref={canvasRef} className="cyber-canvas-3d" />
}
