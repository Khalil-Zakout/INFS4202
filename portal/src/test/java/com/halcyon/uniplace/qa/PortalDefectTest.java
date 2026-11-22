package com.halcyon.uniplace.qa;

import com.halcyon.uniplace.domain.Application;
import com.halcyon.uniplace.domain.ApplicationState;
import com.halcyon.uniplace.domain.Company;
import com.halcyon.uniplace.domain.CompanyStatus;
import com.halcyon.uniplace.domain.Posting;
import com.halcyon.uniplace.domain.Standing;
import com.halcyon.uniplace.domain.Student;
import com.halcyon.uniplace.domain.User;
import com.halcyon.uniplace.engine.EngineClient;
import com.halcyon.uniplace.engine.EngineDtos.AllowanceLine;
import com.halcyon.uniplace.engine.EngineDtos.AllowanceResult;
import com.halcyon.uniplace.engine.EngineDtos.MatchResult;
import com.halcyon.uniplace.engine.MatchScoreService;
import com.halcyon.uniplace.service.ApplicationService;
import com.halcyon.uniplace.service.BusinessRuleException;
import com.halcyon.uniplace.service.CompanyService;
import com.halcyon.uniplace.service.OfferForm;
import com.halcyon.uniplace.service.OfferService;
import com.halcyon.uniplace.service.StudentService;
import com.halcyon.uniplace.support.IntegrationTest;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.mock.mockito.MockBean;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

/**
 * White-box reproduction tests for the Portal defects (see docs/test-cases.md and the GitHub issues).
 * Each test's oracle is the Requirements document; a test that FAILS on this build is the evidence for
 * the defect named in its Javadoc. They are expected to pass once the vendor fixes the defect.
 */
class PortalDefectTest extends IntegrationTest {

    @Autowired ApplicationService applicationService;   // named to avoid shadowing IntegrationTest.applications (the repository)
    @Autowired StudentService studentService;
    @Autowired CompanyService companyService;
    @Autowired OfferService offers;
    @Autowired MatchScoreService matchScores;
    @MockBean EngineClient engine;

    private static final AllowanceResult ANY_ALLOWANCE =
            new AllowanceResult(new BigDecimal("9000.00"), List.of(new AllowanceLine("Total", new BigDecimal("9000.00"))));

    /** APP-02: a WITHDRAWN application is not active and must not count against the student's limit. Issue: D21. */
    @Test
    void withdrawnApplicationsAreNotCountedAsActive() {
        Company c = company("QTech", CompanyStatus.APPROVED);
        Student s = student("3.00", List.of("Java"));
        application(s, openPosting(c, "A", List.of("Java"), 1), ApplicationState.SUBMITTED, 60);
        application(s, openPosting(c, "B", List.of("Java"), 1), ApplicationState.WITHDRAWN, 60);

        assertEquals(1L, applicationService.countActive(s),
                "APP-02: WITHDRAWN is not an active state, so only the SUBMITTED application counts");
    }

    /** APP-02: a student on probation may hold at most 2 active applications. Issue: D22. */
    @Test
    void probationStudentLimitIsTwo() {
        Student probation = student("1.80", List.of("Excel"));
        assertEquals(Standing.PROBATION, probation.getStanding());
        assertEquals(2, applicationService.activeLimitFor(probation),
                "APP-02: the probation active-application limit from Settings is 2, not the GOOD limit");
    }

    /** STU-03: standing is recomputed whenever the Coordinator updates the GPA. Issue: D25. */
    @Test
    void loweringGpaBelowTwoSetsProbation() {
        Student s = student("3.00", List.of("Excel"));
        studentService.updateAcademicRecord(s.getId(), new BigDecimal("1.50"), 60, 0, null);
        assertEquals(Standing.PROBATION, students.findById(s.getId()).orElseThrow().getStanding(),
                "STU-03: GPA 1.50 is below 2.00, so standing must become PROBATION");
    }

    /** COM-03: company names are unique ignoring case and surrounding spaces, on rename too. Issue: D26. */
    @Test
    void renamingToAnExistingNameInAnotherCaseIsRefused() {
        company("Alpha Tech", CompanyStatus.APPROVED);
        User recruiterB = recruiter(company("Beta Tech", CompanyStatus.APPROVED));
        assertThrows(BusinessRuleException.class,
                () -> companyService.update(recruiterB, " alpha tech ", "Technology", "hr@beta.qa"),
                "COM-03: 'alpha tech' collides with 'Alpha Tech' ignoring case and spaces");
    }

    /** COM-02: while a company is suspended its applications are frozen (no state changes). Issue: D04. */
    @Test
    void suspendedCompanyApplicationsAreFrozen() {
        Company c = company("Suspended Co", CompanyStatus.APPROVED);
        Posting p = openPosting(c, "Intern", List.of("Java"), 1);
        User recruiter = recruiter(c);
        Application a = application(student("3.00", List.of("Java")), p, ApplicationState.SUBMITTED, 85);
        companyService.suspend(c.getId());

        assertThrows(BusinessRuleException.class, () -> applicationService.reject(recruiter, a.getId()),
                "COM-02: a suspended company's applications cannot change state until it is approved again");
    }

    /** OFF-02: the response deadline is 72 hours after the offer, keeping the time of day. Issue: D23. */
    @Test
    void offerDeadlineKeepsTheTimeOfDay() {
        LocalDateTime issued = LocalDateTime.of(2026, 11, 20, 13, 30);
        assertEquals(issued.plusHours(72), offers.responseDeadline(issued),
                "OFF-02: 72 hours after 20/11 13:30 is 23/11 13:30, not 23/11 00:00");
    }

    /** OFF-03: when the last seat is taken the posting's other active applications become REJECTED. Issue: D02. */
    @Test
    void fillingThePostingRejectsTheOtherActiveApplications() {
        when(engine.allowance(any())).thenReturn(ANY_ALLOWANCE);
        Company c = company("Fill Co", CompanyStatus.APPROVED);
        Posting p = openPosting(c, "One Seat", List.of("Java"), 1);
        User recruiter = recruiter(c);
        Student s1 = student("3.00", List.of("Java"));
        Student s2 = student("3.00", List.of("Java"));
        User u1 = studentUser(s1);
        Application a1 = application(s1, p, ApplicationState.INTERVIEW, 80);
        Application a2 = application(s2, p, ApplicationState.INTERVIEW, 70);

        OfferForm form = new OfferForm();
        form.setMonthlyAllowance(p.getMonthlyAllowance());
        form.setStartDate(p.getStartDate());
        form.setEndDate(p.getEndDate());
        form.setWeeklyHours(p.getWeeklyHours());
        var offer = offers.issue(recruiter, a1.getId(), form);
        offers.accept(u1, offer.getId());

        assertEquals(ApplicationState.REJECTED, applicationService.get(a2.getId()).getState(),
                "OFF-03: once the posting is FILLED its remaining active applications must be REJECTED");
    }

    /** APP-04: the match score depends on the student's own skills, not only on the posting. Issue: D01. */
    @Test
    void matchScoreIsNotSharedBetweenStudents() {
        when(engine.match(any())).thenAnswer(inv -> {
            var req = (com.halcyon.uniplace.engine.EngineDtos.MatchRequest) inv.getArgument(0);
            boolean strong = req.studentSkills.stream().anyMatch(s -> s.equalsIgnoreCase("Excel"));
            return new MatchResult(strong ? 100 : 35, List.of(), List.of(), List.of());
        });
        Posting p = openPosting(company("Match Co", CompanyStatus.APPROVED), "Supply", List.of("Excel", "SQL"), 2);

        int weak = matchScores.score(List.of("SQL"), p);             // first applicant, low fit
        int strong = matchScores.score(List.of("Excel", "SQL"), p);  // second applicant, high fit

        assertEquals(35, weak);
        assertNotEquals(weak, strong,
                "APP-04: a second student's score must reflect their own skills, not the first student's cached value");
        assertEquals(100, strong);
    }
}
