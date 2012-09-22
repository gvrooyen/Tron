/*
 * Reference Counted Pointer Class
 * Copyright (C) J.A. du Preez
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 *
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * Lesser General Public License for more details.
 *
 *
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
 *
 */

/*
  $Id: rcptr.hpp 96 2005-01-19 13:07:51Z bholt $
*/

/*******************************************************************************
              AUTHOR: J.A du Preez (Copyright exists, all rights reserved.)
*******************************************************************************/

#ifndef RCPTR_HPP
#define RCPTR_HPP

// standard libraries
#include <iostream>  // ostream

using namespace std;

/**
This class implements a Reference Counted Pointer to an object -
it is used similar to a built-in pointer, but is much safer.
Semantically it is related to the "handle" used in JAVA.\\

{\bfADVANTAGES over standard pointers:}\\

(a) Copying or assigning RCPtr's provide safe control over the
lifetime of the commonly pointed to object. (Only the last surviving
RCPtr will destroy the common object.) No multiple deletes or
who's the boss problems!\\

(b) You never explicitly delete memory pointed to by this class, it will
automatically apply a type of garbage collection. You use it and forget
it. No memory leaks!

(c) RCPtr's are initialised to 0 if nothing else is provided.
No dangling pointers!

(d) The ++ and -- operations are disabled, this is a pointer, not an array!\\

{\bfDIFFERENCES with standard pointers:}\\

(a) Conversion to higher level (less derived) RCPtr's are done via constructors
which creates temporary objects pointing to the same data. This is typically transparent
but consider:\\

    void func( RCPtr<Base>& ){implementation...}\\

    RCPtr<Derived> d; func(d) \\

Problem is that a temporary RCPtr<Base> will be created. Although this is fine,
the compiler will generate a warning. If you want to avoid it, first construct/assign to
a RCPtr<Base>. (No problems with const references).\\

(b) Conversion to lower level (more derived) or conversion from const to non-const RCPtr's
needs to be done explicitly by using the standalone template functions 'dynamicCast', and/or
'constCast' (described elsewhere). NOTE - the small difference in the use of these functions:
dynamicCast<DestType>(sourcePtr) and NOT dynamicCast< RCPtr<DestType> > which is a closer parallel
to the behaviour of the standard dynamic_cast function and similarly for constCast.\\

(c) There is no support for covariant pointer returns - the requirement for it should be
fairly rare, covariant pointer returns are only essential when you use multiple
inheritance and more than one of the multiple parents specify the same virtual function
but with different pointer returns. Use standard pointers where this is essential.
The following will go totally awry when you return RCPtr's - the compiler will (correctly)
simply and utterly refuse to do this (if you don't know what this is, go and read it up or ask). \\

    class Base {
      virtual RCPtr<Base> func(parameters) = 0;
    }; // Base\\

    class Derived : public Base {
      virtual RCPtr<Derived> func(same parameters) {implementation}
    }; // Derived\\

It simply does not know of the implied inheritance relationship between the RCPtr's.
Either use RCPtr<Base> as returne type throughout, or return a naked Derived*
(controlling its own memory) in the derived class (which can then be swallowed by
another RCPtr shortly afterwards).\\

NOTE -  When the info you want returned is already contained in a RCPtr and you
want to transfer that to another RCPtr, detouring via a naked pointer pointing
to a (newly created) copy of the info is somewhat inefficient. (As already discussed
in Warning 1, if you're not working with a new copy and you're doing this, you are
in deep trouble in any case.)\\

WARNING 1: \\
Take the WARNINGS in the RCPtr member documentation (see in class) seriously,
if not your code will CRRROAK in the most horribly spectacular fashion!
In general, when you give a RCPtr control over a naked pointer, that RCPtr, together
with the other RCPtr's that it is AWARE of (i.e. they share a common ref count),
gets ALL control and responsibility for ever and ever amen. A sort of a Kremlin inner
ring of power. NOTE - RCPtr's pointing to the same data are not necessarily AWARE of
each other, that depends on how they were created/assigned. If they are not you will
regret it.) Woe be to you if something else destroys the naked pointer, or if the RCPtr
departs to code heaven too early. That also holds for abusing naked pointers obtained
via the objPtr() and cntPtr members. Be especially wary about the following types of
situations:\\

    { 
      RCPtr<ClassType> aRCPtr; 
      { 
        ClassType anObject; 
        aRCPtr = RCPtr<ClassType> (&anObject);
      }
      When you get here your 'aRCPtr' will be dangling in deep space - (of course
      this is no diffent from normal pointers)
    }\\

    or just as bad:\\

    {
      ClassType anObject; 
      { 
        RCPtr<ClassType> aRCPtr = RCPtr<ClassType> (&anObject);
      }
      When you get here your 'anObject' will be insane
    }\\
NOTE - In general using the address of (&) operator with RCPtr's is bad news.\\    

WARNING 2: Avoid initialising temporary RCPtr's with naked pointers - your naked pointer will
get nuked. (Its playing with the big boys now.) When using RCPtr's as parameters to functions,
keep your eyes peeled for the following gotcha. Say you have a function:\\

    func(const RCPtr<ClassType>& par)\\

startling things may happen if you call it with a naked pointer ie\\

    {
      ClassType* nakedPtr = new ClassType;
      func( RCPtr<ClassType> (nakedPtr) );
    }\\

A temporary RCPtr is created when calling the function. It will destroy nakedPtr when it
auto-destructs, leaving nakedPtr dangling in deep space. NOTE - you have to give your
permission for this mayhem to happen. The constructor using a naked pointer has been
declared as "explicit" (see code). In other words, this constructor will not happen
without you explicitly saying so. And that is the ONLY way for a lonely naked pointer
to get into a RCPtr. Therefore you are fairly safe, it will not sneak up on you - quite
often it is the efficient option to use an existing RCPtr as a parameter to a function.\\

WARNING 3: In spite of all the nice things claimed of the RCPtr, you can still get a
memory leak even while using them! This happens when you get your RCPtrs tied up in a 
loop (a doubly linked list using RCPtrs is one example). Here is the simplest example, 
more elaborate ones are possible too (sketching it may help):\\

    class Type {
    public:
      RCPtr<Type> aPtr;
    }; // Type\\
  
Now (mis)use this class in a piece of code as follows:\\

    RCPtr<Type> extPtr(new Type);
    extPtr->aPtr = extPtr; // both pointers now look at the same object;
    extPtr = 0; // this one's a goner
    // but the internal aPtr won't destruct, it is still looking at something.
    // in other words there's now a memory leak here.\\

Another variant:\\

    RCPtr<Type> ext1Ptr(new Type);
    RCPtr<Type> ext2Ptr(new Type);
    ext1Ptr->aPtr = ext2Ptr; 
    ext2Ptr->aPtr = ext1Ptr; // our pointer loop is now in place
    ext1Ptr = ext2Ptr = 0;   // gone with the wind
    // once again the two aPtr's won't destruct - memory leak!\\

How to fix it? Ok, this is tricky and situation dependend - you got to think carefully
about what you are doing. Have a good look at your loop of RCPtrs and see whether you
can break the loop by replacing certain of them with plain pointers (Yea, I know, you
thought you'll never use them again. Well ...) For instance, in a doubly linked list,
how about replacing the backward links with plain C pointers? That sort of thing.\\

TIP 1: You want to get a naked pointer out of the grips of a RCPtr? Currently there is
no direct support for this. And I can see no safe way of implementing it except to
tell the RCPtr's that they have just experienced a coup-de-tat and must go and sit and
sulk in the corner (or face a firing squad). These types of things, however, tend to
get gory and really mess existing states up. However, if you use the objPtr() member
you can get to the naked pointer, just remember that you may not control its lifetime.
And you can get a NEW/safe naked pointer by using a copy constructor to do
something like:\\

    ClassType* nakedPtr = new ClassType(*aRCPtr);\\

or if something like a copy/clone member is supported\\

    ClassType* nakedPtr = rcPtr->copy();\\

TIP 2:
As with all pointers, copies of any sort are shallow. In keeping with a minimalist
spirit, no support is provided for deep copies. Do this by using the copy constructor 
of the underlying object on the dereference eg: \\
    T deep(*shallowRCPtr);           // construct from underlying object \\
Remember that if the copy constructor also was shallow you will have to deepen that too ie:
    deep.deepen();\\

TIP 3:
Play with rcptr.eg.cc for an example of typical use. It compiles standalone.

*/

template<class T>
class RCPtr {

  //============================ Traits and Typedefs ============================
  
  //======================== Constructors and Destructor ========================
public:

  ///Default constructor, points to an nil object
  RCPtr();

  /**
   * Copy constructor, both RCPtr's now point to the same underlying object
   * and are aware of each other.
   */
  RCPtr(const RCPtr& rcp);

  /**
   * Copy constructor from a lower type RCPtr, both now point to the same underlying object
   * and are aware of each other.
   */
  template <class FromType>
  RCPtr(const RCPtr<FromType>& rcp);

  ///Destructor, will not destroy the actual object if another RCPtr references it.
  ~RCPtr();

  /**
   * {\em WARNING:} Takes over lifetime control. You hereby solemnly swear that nothing external will 
   * ever try to destroy justNewed. RCPtr may, however, destroy it whenever it deems necessary.
   * NOTE: Via this constructor the RCPtr has no knowledge of anything else (including other
   * RCPtr's) that may also lay claim to justNewed - a sure recipe for chaos! Can construct with NIL.
   */
  explicit RCPtr(T* justNewed);

  /**
   * Low-level constructor to Share the pointed-to object with another (compatible)
   * reference counting class.
   * The RCPtr and the other ref count class now point to the same underlying object
   * and are aware of each other. Useful for implementing a type of upcasting between
   * RCPtr's, but also allows ref counted sharing with potentially quite different
   * ref count classes. Recommended to prefer higher-level constructors.
   */
  RCPtr(T* objectPtr,
        unsigned* countPtr);

  //========================= Operators and Conversions =========================
public:
  
  /**
   * Assignment, both RCPtr's now point to the same underlying object and
   * are aware of each other.
   */
  RCPtr& operator=(const RCPtr& rhs);

  /**
   * Assignment, both RCPtr's now point to the same underlying object and
   * are aware of each other.
   */
  template <class FromType>
  RCPtr<T>& operator=(const RCPtr<FromType>& rhs);
  
  ///Very handy to access all the members of the underlying object via ->
  T* operator->() const;

  ///Dereferencing also works
  T& operator*() const;

  ///For boolean comparisons
  operator bool() const;
  
  /**
   * Low-level assignment from another compatible reference counted object
   * (including RCPtr's), both now point to the same underlying object and
   * are aware of each other. Recommend to prefer the (safer) higher-level
   * members.
   */
  RCPtr& assignFrom(T* objectPtr,
                    unsigned* countPtr);

  //================================= Iterators =================================
  
  //============================= Exemplar Support ==============================
// there is nothing here because this class is not decended from ExemplarObject
  
  //=========================== Inplace Configuration ===========================
  
  //===================== Required Virtual Member Functions =====================
  
  //====================== Other Virtual Member Functions =======================
  
  //======================= Non-virtual Member Functions ========================
public:
  
  /**
   * Return the pointer that this object encapsulates.
   * {\em WARNING:} Please do not pass this returned pointer around 
   * or abuse (e.g. delete) it. If you don't understand the issues 
   * involved then rather refrain from using this call or ask someone
   * to explain it to you.
   */
  T* objPtr() const;

  /**
   * Return the counts pointer containing the reference counts.
   * {\em WARNING:} Please do not pass this returned pointer around 
   * or abuse (e.g. delete) it. If you don't understand the issues 
   * involved then rather refrain from using this call or ask someone
   * to explain it to you.
   */
  unsigned* cntPtr() const;

  /**
   * The pointed to object will now never be destroyed by the RCPtr. This
   * is useful if you want to assign the address of an existing object,
   * BUT {\em WARNING:} USE WITH EXTREME CARE, taking the address of an
   * existing object is dangerous stuff. The onus is now on YOU to make
   * absolutely sure that the existing object will not expire too early
   * (dangling RCPtr) or too late (memory leak)! Also note, this method
   * only holds for the currently pointed to object. Should you assign
   * a new one, it is a whole new ball-game.
   */
  void makeImmortal();
  
  ///true if object shared with other RCPtr's
  bool shared() const;

  //================================== Friends ==================================
public:

  /**
   * Dynamically checked cast to different type RCPtr.
   * Usage: toTypePtr = dynamicCast<ToType> (fromPtr)
   * NOTE - caller needs to check for success
   * @param fromPtr The source type RCPtr.
   * @return The casted RCPtr - 0 if failed.
   */
  template<class ToType, class FromType>
  friend RCPtr<ToType> dynamicCast(const RCPtr<FromType>& fromPtr);

  /**
   * Casting constness away from a RCPtr.
   * Usage: nonConstPtr = constCast<ToType> (fromPtr)
   * @param fromPtr The source type RCPtr.
   * @return The const casted RCPtr.
   */
  template<class ToType, class FromType>
  friend RCPtr<ToType> constCast(const RCPtr<FromType>& fromPtr);

  /**
   * Dynamically checked assignment implementing toPtr = fromPtr inplace.
   * Remember: assignTo(lhs, rhs) as in lhs = rhs;
   * NOTE - caller needs to check for success
   * Slightly more efficient than a dynamicCast operator= combination.
   * @param toPtr The destination type RCPtr.
   * @param fromPtr The source type RCPtr.
   * @return toPtr - The casted RCPtr - 0 if failed.
   * @return true if succesful 
   */
  template<class ToType, class FromType>
  friend bool assignTo(RCPtr<ToType>& toPtr,
                       const RCPtr<FromType>& fromPtr);

  ///Can output it
  // friend ostream& operator<< <>(ostream& file,
  //                              const RCPtr<T>& rcp);
  
  //=============================== Data Members ================================
private:
  
  T* oPtr;
  unsigned* cPtr;

  //============================ DEPRECATED Members =============================

  
}; // RCPtr

#include "rcptr.tcc"

#endif // RCPTR_HPP


//============================= CVS DOCUMENTATION =============================

/*
  $Log: rcptr.hpp,v $
  Revision 1.1  2004/09/13 14:02:06  jcronje
  Moved header files into the includes/sdr directory

  Revision 1.5  2003/11/19 12:53:00  jcronje
  This class in now licensed under the LGPL

  Revision 1.34  2003/06/17 15:53:33  dupreez
  Added some comments about RCPtr deadlock loops [JAdP]

  Revision 1.33  2003/05/08 12:17:12  dupreez
  Some updates on the way to g++ v3 compatibility [JADP]

  Revision 1.32  2002/12/23 14:14:20  dupreez
  Cosmetic changes [JAdP]

  Revision 1.31  2002/11/28 11:06:04  edward
  cosmetic (section headings and doc++ to doxygen conversion) [EdV]

  Revision 1.30  2002/09/12 16:16:37  edward
  cosmetic [EdV]

  Revision 1.29  2002/09/12 12:09:14  edward
  cosmetic [EdV]

  Revision 1.28  2002/08/19 10:38:54  dupreez
  Removing/commenting includes [EdV]

  Revision 1.27  2002/05/31 14:23:09  dupreez
  Moved code out of .hpp files [EdV]

  Revision 1.26  2002/03/12 12:25:50  dupreez
  Cosmetic changes

  Revision 1.25  2001/07/16 08:50:59  dupreez
  Added a member to prevent RCPtr from EVER destroying its internal object

  Revision 1.24  2001/04/17 13:29:08  dupreez
  Andre dT added code to check for null pointers when DEBUG_MODE

  Revision 1.23  2001/02/19 12:33:51  dupreez
  destructor sets raw pointers equal to 0

  Revision 1.22  2001/02/08 07:22:19  dupreez
  Renamed the castTo member to dynamicCast. Added a constCast member.

  Revision 1.21  2001/02/06 07:59:14  dupreez
  Cosmetic

  Revision 1.20  2001/02/05 04:42:09  dupreez
  Extensive support for inheritance hierarchies. Also added a 'castTo'
  which follows the behaviour of the built-in 'dynamic_cast'.

  Revision 1.19  2001/02/01 08:10:41  dupreez
  dotting i's and crossing t's

  Revision 1.18  2001/01/31 09:33:30  dupreez
  Updated the documentation

  Revision 1.17  2001/01/30 15:14:16  dupreez
  The upgraded RCPtr -

  Functionality no longer supported (stricter):
    the implicit conversion to the underlying pointer is a goner.
    assignment of a raw pointer also is no more - use the appropriate constructor.

  New functionality:
    Now provides some support for inheritance/casts.
    Also can share common data with other types of objects that support reference
    counting.

  Revision 1.15  2001/01/15 13:08:55  dupreez
  Added documentation

  Revision 1.14  2000/12/01 12:49:14  dupreez
  Cosmetic

  Revision 1.13  2000/09/20 18:19:04  dupreez
  Cosmetic

  Revision 1.12  2000/08/21 10:32:42  goof
  Added asPtr() call that returns the wrapped pointer. This should be used
  instead of the T* operator () call to obtain the pointer. T* operator () is
  scheduled for deprecation soon.

  Revision 1.11  2000/05/26 06:40:44  dupreez
  Correct teeny-weeny spelling mistake in documentation.

  Revision 1.10  2000/05/20 16:50:35  dupreez
  The constructor from a naked pointer in RCPtr is now declared explicit.
  Modified Files:
   	rcptr.hpp triarand.hpp arrpdf_txn.cc bwreest_txn.cc
   	hmm_text.cc trnfit_txn.cc

  Revision 1.9  2000/04/29 11:20:33  dupreez
  Rectified small bug in description of shared() member

  Revision 1.8  2000/04/28 15:29:11  dupreez
  Sluit vlaggies in sodat CVS weergawe inligting kan stoor.

*/
