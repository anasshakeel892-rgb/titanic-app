import "./globals.css";

export const metadata = {
  title: "RMS Titanic — Survival Predictor",
  description: "A full-stack Titanic survival predictor backed by a real trained model",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="min-h-screen font-sans antialiased">{children}</body>
    </html>
  );
}
