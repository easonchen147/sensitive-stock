import Link from "next/link";

interface SymbolLinkProps {
  symbol: string;
  name?: string;
  className?: string;
}

export function SymbolLink({ symbol, name, className = "" }: SymbolLinkProps) {
  return (
    <Link
      href={`/diagnosis?symbol=${encodeURIComponent(symbol)}`}
      className={`font-mono hover:text-primary hover:underline transition-colors ${className}`}
    >
      {name ? `${symbol} ${name}` : symbol}
    </Link>
  );
}
