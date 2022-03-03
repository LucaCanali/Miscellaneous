package ch.cern.udf

import org.apache.spark.sql.api.java._
import scala.math.{abs, cos, cosh, sin, sinh, sqrt}

class DimuonMass extends UDF6[Float, Float, Float, Float, Float, Float, Float] {
  def call(m0_pt: Float, m0_eta: Float, m0_phi: Float, m1_pt: Float, m1_eta: Float, m1_phi: Float): Float = {
    val E = sqrt(2 * m0_pt * m1_pt * (cosh(m0_eta - m1_eta) - cos(m0_phi - m1_phi)))

    E.toFloat
  }
}

