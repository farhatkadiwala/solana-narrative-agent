"use client";

export default function Error({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center px-6">
      <div className="text-center max-w-md">
        <p className="text-[72px] font-bold text-title tracking-[-3px] leading-none">
          500
        </p>
        <p className="text-[19px] font-medium text-title tracking-[-0.95px] mt-4">
          Something went wrong
        </p>
        <p className="text-[15px] text-desc tracking-[-0.75px] leading-[1.12] mt-2">
          An unexpected error occurred. Please try again.
        </p>
        <button
          onClick={reset}
          className="inline-block mt-6 px-5 py-2.5 bg-hero text-white text-sm font-medium tracking-[-0.28px] rounded-md hover:opacity-85 transition-opacity cursor-pointer"
        >
          Try again
        </button>
      </div>
    </div>
  );
}
