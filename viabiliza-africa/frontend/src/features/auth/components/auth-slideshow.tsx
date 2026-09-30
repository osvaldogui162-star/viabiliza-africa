import Image from "next/image";

import { BRAND_SLIDE_HERO } from "@/lib/constants/brand-slides";

function AuthSlideOverlays() {
  return (
    <>
      <div className="pointer-events-none absolute inset-0 bg-[#030c0a]/12" aria-hidden />
      <div
        className="pointer-events-none absolute inset-0 bg-gradient-to-t from-[#030c0a]/38 via-[#071612]/10 to-transparent"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute inset-0 bg-gradient-to-r from-[#030c0a]/16 via-transparent to-[#030c0a]/18"
        aria-hidden
      />
    </>
  );
}

export function AuthSlideshow() {
  return (
    <section
      className="auth-slideshow relative hidden h-dvh max-h-dvh overflow-hidden bg-[#064e45] lg:flex lg:flex-col"
      aria-hidden
    >
      <div className="absolute inset-0 overflow-hidden">
        <Image
          src={BRAND_SLIDE_HERO}
          alt=""
          fill
          priority
          unoptimized
          sizes="(min-width: 1536px) 50vw, (min-width: 1024px) 50vw, 0px"
          className="auth-slide-branded auth-slide-branded--auth"
          draggable={false}
        />
      </div>
      <AuthSlideOverlays />
    </section>
  );
}

export function AuthSlideshowMobile() {
  return (
    <div className="auth-slideshow-mobile relative mb-4 aspect-[16/10] w-full overflow-hidden rounded-xl sm:aspect-[16/9] lg:hidden">
      <div className="absolute inset-0 overflow-hidden">
        <Image
          src={BRAND_SLIDE_HERO}
          alt=""
          fill
          priority
          unoptimized
          sizes="100vw"
          className="auth-slide-branded auth-slide-branded--mobile"
          draggable={false}
        />
      </div>
      <AuthSlideOverlays />
    </div>
  );
}
