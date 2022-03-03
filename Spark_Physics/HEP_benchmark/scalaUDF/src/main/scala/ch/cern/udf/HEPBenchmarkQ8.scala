package ch.cern.udf

//
// This implements Scala UDFs for the HEP benchmark using Apache Spark
// See https://github.com/LucaCanali/Miscellaneous/Spark_Physics
//

import scala.math.Pi
import org.apache.spark.sql.api.java.UDF4
import org.apache.spark.sql.Row
// import scala.math.{abs, cos, cosh, sin, sinh, sqrt}
import net.jafama.FastMath.{abs, cos, cosh, sin, sinh, sqrt} // use faster math libraries


//
// This is used by the solution to Q8: Filter in Spark, process in Scala UDF
//

case class LorentzPtEtaPhiMCharge(Pt: Float, Eta: Float, Phi: Float, M: Float, Charge: Int)

class diLeptonMt extends UDF4[Seq[Row], Seq[Row], Float, Float, Float] {
  def call(muons: Seq[Row], electrons: Seq[Row], met_pt: Float, met_phi: Float): Float = {

    // restructure input into Lorentz vector Lists
    val lorentzMuons = muons map {
      case Row(pt: Float, eta: Float, phi: Float, m: Float, charge: Int) =>
        LorentzPtEtaPhiMCharge(pt, eta, phi, m, charge)
    }
    val lorentzElectrons = electrons map {
      case Row(pt: Float, eta: Float, phi: Float, m: Float, charge: Int) =>
        LorentzPtEtaPhiMCharge(pt, eta, phi, m, charge)
    }
    val allLeptons = (lorentzMuons.toList ++ lorentzElectrons.toList)

    // group into same-flavor 2-lepton pairs with opposite charge
    val lorentzDimuons = lorentzMuons.combinations(2).filter(x => x(0).Charge != x(1).Charge).toList
    val lorentzDielectrons = lorentzElectrons.combinations(2).filter(x => x(0).Charge != x(1).Charge).toList
    val lorentzDileptons = lorentzDimuons ++ lorentzDielectrons

    // execute the rest of the computation in case there are dilepton pairs with the desired characteristics
    if (lorentzDileptons.length >= 1) {
      // find the lepton pair with mass closer to 91.2 GeV
      val dileptonMasses = for (l <- lorentzDileptons) yield (abs(invariantMassPtEtaPhiM(l) - 91.2f))
      val indexDilepton = dileptonMasses.zipWithIndex.min._2
      val selectedDilepton = lorentzDileptons(indexDilepton)

      // max Pt of the "other leptons" (other than the pair selected above)
      val otherLeptons = allLeptons filter (_ != selectedDilepton(0)) filter (_ != selectedDilepton(1))
      if (! otherLeptons.isEmpty) {
        val selectedOtherLeptonsIndex = otherLeptons.map(_.Pt).zipWithIndex.max._2

        // compute the request transverse mass value, by crossing MET with the leading lepton.
        val deltaPhi = (met_phi - otherLeptons(selectedOtherLeptonsIndex).Phi + Pi) % (2 * Pi) - Pi

        val transverseMass = sqrt(2.0f * met_pt * otherLeptons(selectedOtherLeptonsIndex).Pt *
          (1.0f - cos(deltaPhi))).toFloat

        transverseMass
      }
      else -1f
    }
    else -1f
  }

  // Compute the invariant mass
  // See also https://en.wikipedia.org/wiki/Invariant_mass
  def invariantMassPtEtaPhiM(particlesPtEtaPhiM: Seq[LorentzPtEtaPhiMCharge]): Float = {

    val particlesPxPyPzE = particlesPtEtaPhiM map {x =>
      PtEtaPhiM2PxPyPzE(x)
    }
    val sumMomenta = particlesPxPyPzE.reduce(add)
    val mass = sqrt(sumMomenta.E * sumMomenta.E - sumMomenta.Px * sumMomenta.Px - sumMomenta.Py * sumMomenta.Py - sumMomenta.Pz * sumMomenta.Pz).toFloat
    mass
  }

  // Add two Lorentz vectors
  def add(p1: LorentzPxPyPzE, p2: LorentzPxPyPzE): LorentzPxPyPzE = {
    LorentzPxPyPzE(p1.Px + p2.Px, p1.Py + p2.Py, p1.Pz + p2.Pz, p1.E + p2.E)
  }

  // Convert a Lorentz vector from (Pt Eta Phi M) to (Px, Py, Pz, E)
  def PtEtaPhiM2PxPyPzE(in: LorentzPtEtaPhiMCharge): LorentzPxPyPzE = {
    val out = LorentzPxPyPzE(
      in.Pt * cos(in.Phi).toFloat,
      in.Pt * sin(in.Phi).toFloat,
      in.Pt * sinh(in.Eta).toFloat,
      sqrt((in.Pt * cosh(in.Eta)*(in.Pt * cosh(in.Eta)) + in.M * in.M)).toFloat
    )
    out
  }
}
