import "./styles.css";

export const metadata = {
  title: "AutoAssist",
  description: "Atención postventa DINAMEX",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
