import {
  motion,
  useReducedMotion,
  useScroll,
  useTransform,
  type MotionValue,
} from "motion/react";
import { Fragment, useRef } from "react";

interface TaglineRevealProps {
  id?: string;
  lines: string[];
}

function Word({
  children,
  progress,
  range,
  animate,
}: {
  children: string;
  progress: MotionValue<number>;
  range: [number, number];
  animate: boolean;
}) {
  const opacity = useTransform(progress, range, [0.22, 1]);
  return (
    <motion.span className="tagline__word" style={animate ? { opacity } : undefined}>
      {children}
    </motion.span>
  );
}

export function TaglineReveal({ id, lines }: TaglineRevealProps) {
  const ref = useRef<HTMLHeadingElement>(null);
  const reduceMotion = useReducedMotion();
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start 0.85", "end 0.5"],
  });

  const lineWords = lines.map((line) => line.split(" "));
  const total = lineWords.reduce((sum, words) => sum + words.length, 0);
  let index = 0;

  return (
    <h2 id={id} ref={ref} className="tagline__text">
      {lineWords.map((words, lineIndex) => (
        <span className="tagline__line" key={lines[lineIndex]}>
          {words.map((word) => {
            const range: [number, number] = [index / total, (index + 1) / total];
            index += 1;
            return (
              <Fragment key={`${word}-${index}`}>
                <Word progress={scrollYProgress} range={range} animate={!reduceMotion}>
                  {word}
                </Word>{" "}
              </Fragment>
            );
          })}
        </span>
      ))}
    </h2>
  );
}
