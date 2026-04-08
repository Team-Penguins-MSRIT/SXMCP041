import { useMemo, useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import * as THREE from 'three'

function RotatingLattice() {
  const group = useRef<THREE.Group>(null)
  const geo = useMemo(() => new THREE.IcosahedronGeometry(2.6, 2), [])
  useFrame((_, delta) => {
    if (!group.current) return
    group.current.rotation.x += delta * 0.06
    group.current.rotation.y += delta * 0.09
  })

  return (
    <group ref={group}>
      <mesh geometry={geo}>
        <meshBasicMaterial
          color="#312e81"
          wireframe
          transparent
          opacity={0.14}
        />
      </mesh>
      <mesh geometry={geo} scale={0.92}>
        <meshBasicMaterial
          color="#4c1d95"
          wireframe
          transparent
          opacity={0.08}
        />
      </mesh>
    </group>
  )
}

export default function ParticleCanvas() {
  return (
    <div className="pointer-events-none fixed inset-0 z-0 opacity-90">
      <Canvas
        camera={{ position: [0, 0, 7.5], fov: 55 }}
        gl={{ alpha: true, antialias: true }}
        dpr={[1, 2]}
      >
        <ambientLight intensity={0.4} />
        <RotatingLattice />
      </Canvas>
    </div>
  )
}
