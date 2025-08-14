import React, { useEffect, useRef, useState } from "react";

const SymbolicLifeBar = () => {
  const [pulse, setPulse] = useState(0);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");

    if (!canvas || !ctx) return;

    canvas.width = 400;
    canvas.height = 50;

    let x = 0;
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.beginPath();
      ctx.moveTo(0, canvas.height / 2);

      for (let i = 0; i < canvas.width; i++) {
        const y = canvas.height / 2 + Math.sin(i * 0.05 + pulse) * 10;
        ctx.lineTo(i, y);
      }

      ctx.strokeStyle = "#00ff66";
      ctx.lineWidth = 2;
      ctx.stroke();
      setPulse(p => p + 0.1);
    };

    const interval = setInterval(draw, 60);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h3>Symbolic Life Pulse</h3>
      <canvas ref={canvasRef} style={{ border: "1px solid #222" }} />
    </div>
  );
};

export default SymbolicLifeBar;
