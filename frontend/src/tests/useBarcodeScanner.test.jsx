import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, fireEvent, screen } from "@testing-library/react";
import { useRef } from "react";
import { useBarcodeScanner } from "../shared/hooks/useBarcodeScanner";

function Harness({ onScan, enabled = true }) {
  const barcodeRef = useBarcodeScanner({ onScan, enabled });
  const otherRef = useRef(null);
  return (
    <div>
      <input ref={barcodeRef} data-testid="barcode-input" defaultValue="" />
      <input ref={otherRef} data-testid="other-input" />
    </div>
  );
}

function fireScan(code, target) {
  for (const ch of code) {
    fireEvent.keyDown(target, { key: ch });
  }
  fireEvent.keyDown(target, { key: "Enter" });
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

describe("useBarcodeScanner", () => {
  let onScan;
  let renderResult;

  beforeEach(() => {
    onScan = vi.fn();
    renderResult = render(<Harness onScan={onScan} />);
  });

  afterEach(() => {
    renderResult.unmount();
  });

  it("scans a fast-typed barcode even when focus is elsewhere", () => {
    fireScan("6291041500213", document.body);
    expect(onScan).toHaveBeenCalledTimes(1);
    expect(onScan).toHaveBeenCalledWith("6291041500213");
  });

  it("reads the barcode value when Enter is pressed in the barcode input", () => {
    const input = screen.getByTestId("barcode-input");
    fireEvent.change(input, { target: { value: "12345" } });
    fireEvent.keyDown(input, { key: "Enter" });
    expect(onScan).toHaveBeenCalledTimes(1);
    expect(onScan).toHaveBeenCalledWith("12345");
  });

  it("ignores slow manual typing in another field", async () => {
    const input = screen.getByTestId("other-input");
    fireEvent.keyDown(input, { key: "a" });
    await sleep(60);
    fireEvent.keyDown(input, { key: "b" });
    await sleep(60);
    fireEvent.keyDown(input, { key: "Enter" });
    expect(onScan).not.toHaveBeenCalled();
  });

  it("ignores empty and repeated Enter", () => {
    fireEvent.keyDown(document.body, { key: "Enter" });
    fireEvent.keyDown(document.body, { key: "Enter", repeat: true });
    expect(onScan).not.toHaveBeenCalled();
  });

  it("clears the buffer after a successful scan", () => {
    fireScan("111", document.body);
    fireEvent.keyDown(document.body, { key: "Enter" });
    expect(onScan).toHaveBeenCalledTimes(1);
  });

  it("does nothing while disabled", () => {
    renderResult.unmount();
    const { unmount } = render(<Harness onScan={onScan} enabled={false} />);
    fireScan("999", document.body);
    expect(onScan).not.toHaveBeenCalled();
    unmount();
  });

  it("ignores non-character keys and modifiers during a scan", () => {
    fireEvent.keyDown(document.body, { key: "6" });
    fireEvent.keyDown(document.body, { key: "Backspace" });
    fireEvent.keyDown(document.body, { key: "2" });
    fireEvent.keyDown(document.body, { key: "Shift" });
    fireEvent.keyDown(document.body, { key: "Enter" });
    expect(onScan).toHaveBeenCalledWith("62");
  });
});
