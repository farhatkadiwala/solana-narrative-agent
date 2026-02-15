import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center px-6">
      <div className="text-center max-w-md">
        <p className="text-[72px] font-bold text-title tracking-[-3px] leading-none">
          404
        </p>
        <p className="text-[19px] font-medium text-title tracking-[-0.95px] mt-4">
          Page not found
        </p>
        <p className="text-[15px] text-desc tracking-[-0.75px] leading-[1.12] mt-2">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Link
          href="/"
          className="inline-block mt-6 px-5 py-2.5 bg-hero text-white text-sm font-medium tracking-[-0.28px] rounded-md hover:opacity-85 transition-opacity"
        >
          Back to ideas
        </Link>
      </div>
    </div>
  );
}
