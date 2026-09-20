import { useEffect, useRef } from "react";
import { SHAPE_LABELS, SHAPE_PATHS, type ShapeId } from "../lib/shapes";

type Props = {
  options: string[];
  onSelect: (option: string) => void;
  autoFocus?: boolean;
};

export default function ShapeOptions({ options, onSelect, autoFocus = false }: Props) {
  const buttons = useRef<Array<HTMLButtonElement | null>>([]);
  useEffect(() => {
    if (autoFocus) buttons.current[0]?.focus();
  }, [autoFocus, options]);

  const focus = (index: number) => {
    buttons.current[(index + options.length) % options.length]?.focus();
  };
  return (
    <div className="grid w-full max-w-md grid-cols-3 gap-2" role="group" aria-label="Shape choices">
      {options.map((option, index) => {
        const id = option as ShapeId;
        const label = SHAPE_LABELS[id] ?? option;
        return (
          <button
            key={`${option}-${index}`}
            ref={(element) => {
              buttons.current[index] = element;
            }}
            type="button"
            tabIndex={index === 0 ? 0 : -1}
            aria-label={`${index + 1}: ${label}`}
            onClick={() => onSelect(option)}
            onKeyDown={(event) => {
              if (event.key >= "1" && event.key <= "6") {
                const next = Number(event.key) - 1;
                if (next < options.length) {
                  event.preventDefault();
                  focus(next);
                  onSelect(options[next]!);
                }
              } else if (event.key === "ArrowRight" || event.key === "ArrowDown") {
                event.preventDefault();
                focus(index + 1);
              } else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
                event.preventDefault();
                focus(index - 1);
              } else if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                onSelect(option);
              }
            }}
            className="flex min-h-16 flex-col items-center justify-center gap-1 rounded-xl border border-line bg-surface px-2 py-2 text-sm transition hover:border-accent focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            <svg viewBox="-1 -1 2 2" className="size-8 fill-ink" aria-hidden="true">
              <path d={SHAPE_PATHS[id] ?? ""} />
            </svg>
            <span>{label}</span>
          </button>
        );
      })}
    </div>
  );
}
