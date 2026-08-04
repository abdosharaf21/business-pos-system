import { useEffect, useRef } from "react";

const SCAN_INTERVAL_MS = 50;
const MAX_SCAN_LENGTH = 64;

export function useBarcodeScanner({ onScan, enabled = true }) {
  const onScanRef = useRef(onScan);
  const inputRef = useRef(null);
  const bufferRef = useRef("");
  const lastKeyTimeRef = useRef(0);
  const fastTypingRef = useRef(false);

  useEffect(() => {
    onScanRef.current = onScan;
  }, [onScan]);

  useEffect(() => {
    if (!enabled) return undefined;

    const handleKeyDown = (event) => {
      if (event.repeat || event.ctrlKey || event.metaKey || event.altKey) {
        return;
      }

      if (event.key === "Enter") {
        let barcode = "";
        if (inputRef.current && event.target === inputRef.current) {
          barcode = inputRef.current.value || "";
        } else if (fastTypingRef.current && bufferRef.current) {
          barcode = bufferRef.current;
        }
        bufferRef.current = "";
        fastTypingRef.current = false;

        barcode = barcode.trim();
        if (!barcode) return;
        event.preventDefault();
        onScanRef.current(barcode);
        if (inputRef.current) {
          inputRef.current.value = "";
          inputRef.current.focus();
        }
        return;
      }

      if (event.key.length !== 1) {
        return;
      }

      const now = performance.now();
      const isFast = now - lastKeyTimeRef.current <= SCAN_INTERVAL_MS;
      lastKeyTimeRef.current = now;
      fastTypingRef.current = isFast;

      if (isFast) {
        if (bufferRef.current.length < MAX_SCAN_LENGTH) {
          bufferRef.current += event.key;
        }
      } else {
        bufferRef.current = event.key;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [enabled]);

  return inputRef;
}
