class NorthStarrGenai < Formula
  desc "Your Development Partner — AI-specific workflow for AI coding tools"
  homepage "https://github.com/selcukyucel/north-starr-genai"
  url "https://github.com/selcukyucel/north-starr-genai/archive/refs/tags/v0.15.0.tar.gz"
  sha256 "c99f01a65e3386ab2c99a3a68b8b2931e137882c9625740b4d8aab17182ee9a7"
  license "MIT"

  def install
    bin.install "bin/north-starr-genai"
    (share/"north-starr-genai").install "templates"
    (share/"north-starr-genai").install "skills"
  end

  test do
    system "#{bin}/north-starr-genai", "version"
  end
end
