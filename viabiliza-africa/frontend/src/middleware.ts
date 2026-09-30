import { NextResponse } from "next/server";

import type { NextRequest } from "next/server";



const protectedPaths = ["/dashboard", "/admin", "/projects", "/conta", "/financiador"];



export function middleware(request: NextRequest) {

  const pathname = request.nextUrl.pathname;

  const accessToken = request.cookies.get("va_access_token")?.value;

  const role = request.cookies.get("va_user_role")?.value;



  const requiresAuth = protectedPaths.some((path) => pathname.startsWith(path));

  if (requiresAuth && !accessToken) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }



  if (pathname.startsWith("/admin") && role !== "admin") {
    return NextResponse.redirect(new URL(role === "bank" ? "/financiador" : "/dashboard", request.url));
  }

  if (role === "bank") {
    const allowed =
      pathname.startsWith("/financiador") ||
      pathname === "/login" ||
      pathname.startsWith("/login");
    if (!allowed && accessToken) {
      return NextResponse.redirect(new URL("/financiador", request.url));
    }
  }



  if (pathname === "/login" && accessToken) {
    const redirect = request.nextUrl.searchParams.get("redirect");
    if (redirect && redirect.startsWith("/") && !redirect.startsWith("//")) {
      return NextResponse.redirect(new URL(redirect, request.url));
    }
    const dest = role === "bank" ? "/financiador" : "/dashboard";
    return NextResponse.redirect(new URL(dest, request.url));
  }

  if (pathname === "/signup" && accessToken) {
    const redirect = request.nextUrl.searchParams.get("redirect");
    if (redirect && redirect.startsWith("/") && !redirect.startsWith("//")) {
      return NextResponse.redirect(new URL(redirect, request.url));
    }
    const dest = role === "bank" ? "/financiador" : "/dashboard";
    return NextResponse.redirect(new URL(dest, request.url));
  }

  if (pathname === "/projects/new" && role === "user") {

    return NextResponse.redirect(new URL("/projects", request.url));

  }



  return NextResponse.next();

}



export const config = {

  matcher: [
    "/login",
    "/signup",
    "/dashboard/:path*",
    "/admin",
    "/admin/:path*",
    "/projects/:path*",
    "/conta/:path*",
    "/financiador",
    "/financiador/:path*",
  ],

};


